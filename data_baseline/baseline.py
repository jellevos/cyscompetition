import math
import random
import time

import numpy as np
from Pyfhel import Pyfhel, PyCtxt
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

from sklearn.metrics import roc_auc_score, RocCurveDisplay
from tqdm import tqdm


BANDWIDTH = 8 * 1024 * 1024  # We set the bandwidth to be 1 MB/s (megabyte per second)


def inner_sum(context: Pyfhel, ciphertext: PyCtxt, count: int) -> PyCtxt:
    """
    Sum the `count` values in a packed `ciphertext` and put the result in the first slot. Runs through a binary tree.
    :param context: Encryption context with rotation keys and batching enabled
    :param ciphertext: The ciphertext to sum the values from
    :param count: The number of filled values in the ciphertext, counting from the first slot 'rightwards'
    :return: A ciphertext encrypted the inner sum in the first slot
    """
    result = ciphertext
    for power in reversed(range(math.ceil(math.log2(count)))):
        rotated_result = context.rotate(result, 2**power, True)
        result += rotated_result

    # Mask all values but the first
    plain_mask = [0] * count
    plain_mask[0] = 1
    mask = context.encode(np.array(plain_mask))
    masked_result = context.multiply_plain(result, mask)

    return masked_result


class AccessManager:
    """
    The AccessManager only stores **encrypted** samples, and executes access queries on these.
    """

    def __init__(self, context: Pyfhel):
        """
        An access manager that only stores encrypted data. We hard-code the number of principal components to 6
        :param context: Encryption context (the access manager should only access public keys)
        """
        self._context = context
        self._pca: PCA = None
        self._encoded_components = None
        self._encoded_mean = None
        self._encrypted_user_samples_transformed = []

    def enroll_all_users(self, samples: np.ndarray, user_ids: np.ndarray):
        """
        Enroll all users into the system at once (we are considering a static dataset).
        :param samples: All the separate samples
        :param user_ids: The actual user_id corresponding to each sample
        """

        # Create enough space for all user samples
        user_count = max(user_ids) + 1
        self._encrypted_user_samples_transformed = [None] * user_count

        # Perform a floor division on the chromatograms, losing information but reducing the magnitude of the variables
        # The sensor can also do this pre-processing because it does not rely on the enrolled data
        samples_reduced = samples // 20

        # Perform PCA and keep only the 6 most significant components
        pca = PCA(n_components=6)
        pca.fit(samples_reduced)

        # Select only the 90 highest values in the principal components to limit the magnitude of the final values
        components = pca.components_
        components_abs = np.abs(components)
        top_indices = np.argsort(components_abs)[::-1]
        for i, row in enumerate(top_indices):
            components[i, row[90:]] = 0

        # Multiply the components by 10 and round them down to quantize them.
        components = np.floor(pca.components_ * 10).astype(np.int64)
        pca.components_ = components
        samples_transformed = pca.transform(samples_reduced).astype(np.int64)

        # Save the quantized mean and principal components in encoded form for future computations on encrypted data
        self._encoded_components = [self._context.encode(component) for component in components]
        self._encoded_mean = self._context.encode(np.round(pca.mean_).astype(np.int64))

        # Save the transformed samples per user_id
        for user_id in tqdm(range(user_count)):
            self._encrypted_user_samples_transformed[user_id] = []

            # Encrypt and save each transformed sample
            selected_samples = samples_transformed[user_ids == user_id]
            for selected_sample in selected_samples:
                encrypted_sample = self._context.encryptPtxt(self._context.encode(selected_sample))
                self._encrypted_user_samples_transformed[user_id].append(encrypted_sample)

    def query(self, encrypted_sample: PyCtxt, supposed_user_id: int) -> PyCtxt:
        """
        Queries the database to compute a similarity value. This value is the squared total difference after PCA
        between this `encrypted_sample` and the original encrypted samples belonging to this `supposed_user_id`
        :param encrypted_sample: Encrypted and preprocessed chromatogram of the user :param supposed_user_id: ID that
        this user is trying to grant access for: it is always in the enrolled database :return: Ciphertext encrypting
        the distance/similarity
        """
        # TODO: Write everything in operator overleading?
        # Transform the encrypted_sample according to the principal components
        encrypted_sample -= self._encoded_mean
        sample_multiplied_unpacked = [self._context.multiply_plain(encrypted_sample, self._encoded_components[x], True) for x in range(6)]
        sample_summed_unpacked = [inner_sum(self._context, c, 100) for c in sample_multiplied_unpacked]
        sample_transformed = sample_summed_unpacked[0]
        for i, sample_summed in enumerate(sample_summed_unpacked[1:]):
            sample_transformed += sample_summed >> (i + 1)

        # Select the original samples belonging to this user (already transformed)
        original_samples_transformed = self._encrypted_user_samples_transformed[supposed_user_id]

        # Subtract the transformed sample from the original transformed samples
        subtracted = [original_encrypted_sample - sample_transformed for original_encrypted_sample in
                      original_samples_transformed]

        # Square each subtracted sample and relinearize to bring the ciphertext down to size 2
        squared = [self._context.square(s) for s in subtracted]
        for s in squared:
            self._context.relinearize(s)

        # Sum the squared samples
        # This is an 'outer' sum
        total = squared[0]
        for s in squared[1:]:
            total += s

        # Perform the inner sum of the resulting ciphertext, but more efficiently than in a binary tree
        shifted_1 = self._context.rotate(total, 1, True)
        shifted_1 += total
        shifted_2 = self._context.rotate(shifted_1, 1, True)
        shifted_2 += total
        shifted_5 = self._context.rotate(shifted_2, 3, True)
        shifted_5 += shifted_2

        # Multiply the first element with 1 and the other elements with 0, to make sure no additional information leaks
        mask = self._context.encode(np.array([1, 0, 0, 0, 0, 0, 0, 0, 0]))
        total = self._context.multiply_plain(shifted_5, mask)

        return total


def perform_query(context: Pyfhel, sample: np.ndarray, supposed_user_id: int, access_manager: AccessManager) -> int:
    """

    :param context: Encryption context (the sensor should only access public keys)
    :param sample: Chromatogram of the user
    :param supposed_user_id: ID of the user that this user is trying to grant access for
    :param access_manager: Reference to the access manager to run the query
    :return: Resulting decrypted distance/similarity, if it is above/below a certain threshold access is granted
    """
    # Start the stopwatch (queries may only take 1 second)
    start = time.monotonic()

    # The sensor can perform preprocessing on the sample, but it cannot rely on the data enrolled in the AccessManager
    # We perform a floor division on the chromatograms, losing information but reducing the magnitude of the variables
    sample_reduced = np.floor(sample // 20).astype(np.int64)
    encrypted_sample = context.encryptPtxt(context.encode(sample_reduced))

    # Query the access manager on the encrypted sample. In practice, the response would go to the door.
    encrypted_response = access_manager.query(encrypted_sample, supposed_user_id)

    # The door has access to the secret key, which it uses to decrypt the response
    response = context.decode(context.decrypt(encrypted_response))[0]

    # Assert that the query took at most 1 second
    computation = time.monotonic() - start
    communication = len(encrypted_sample.to_bytes()) + len(encrypted_response.to_bytes())
    if (computation + communication / BANDWIDTH) > 1:
        print(f"Query took too long: {computation + communication / BANDWIDTH} = {computation}s of computation + {communication / 8 / 1024 / 1024}MB of communication")

    return response


# || Prepare data ||
print("Preparing data...")
# Load the user data
X = np.loadtxt("chromatograms.csv", dtype=int, delimiter=',', skiprows=1)
y = np.loadtxt("user_ids.csv", dtype=int, skiprows=1)

# Separate the user data
# The data that the access manager enrolls contains 3 samples for 800 of the 1000 given users ('train' data)
# The data we use to evaluate the access manager consists of the other samples ('test' data)
user_ids_in_database = random.choices(range(1000), k=800)
remaining_user_ids = list(set(range(1000)) - set(user_ids_in_database))

enroll_samples = np.array([[X[5 * user_id + i] for i in range(3)] for user_id in user_ids_in_database]).reshape((800 * 3, 100))
enroll_user_ids = np.repeat(user_ids_in_database, 3)

positive_user_ids = np.array(random.choices(user_ids_in_database, k=200))
positive_samples = np.array([X[5 * user_id + 3] for user_id in positive_user_ids])

negative_user_ids_within = np.array(random.choices(user_ids_in_database, k=100))  # These samples are from users in the dataset pretending to be other users
negative_samples_within = np.array([X[5 * user_id + 4] for user_id in negative_user_ids_within])
negative_user_ids_within = [random.choice(list(set(user_ids_in_database) - {user_id})) for user_id in negative_user_ids_within]

negative_user_ids_outside = np.array(random.choices(remaining_user_ids, k=100))  # These samples are from users outside the dataset
negative_samples_outside = np.array([X[5 * user_id + 4] for user_id in negative_user_ids_outside])
negative_user_ids_outside = np.array(random.choices(user_ids_in_database, k=100))


# || Prepare cryptosystem ||
print("Preparing cryptosystem...")
context = Pyfhel()
context.contextGen(p=786433, m=2**13, flagBatching=True)
context.keyGen()  # Generates both a public and a private key
context.relinKeyGen(50, 1)
context.rotateKeyGen(50)


# || Prepare access manager ||
print("Preparing the access manager...")
# Enroll all users in the access manager
access_manager = AccessManager(context)
access_manager.enroll_all_users(enroll_samples, enroll_user_ids)


# || Evaluate access queries ||
print("Evaluating access queries")
true_labels = np.array(([1] * 200) + ([0] * 200))
resulting_values = []
print("> Evaluating 200 positive samples")
for sample, user_id in tqdm(zip(positive_samples, positive_user_ids), total=200):
    resulting_values.append(perform_query(context, sample, user_id, access_manager))
print("> Evaluating 100 negative samples from within the database")
for sample, user_id in tqdm(zip(negative_samples_within, negative_user_ids_within), total=100):
    resulting_values.append(perform_query(context, sample, user_id, access_manager))
print("> Evaluating 100 negative samples from outside the database")
for sample, user_id in tqdm(zip(negative_samples_outside, negative_user_ids_outside), total=100):
    resulting_values.append(perform_query(context, sample, user_id, access_manager))

resulting_values = np.array(resulting_values)


# || Run scoring ||
print("Running scoring function")

# Take the max so that participants can either output distances or similarities
score_1 = roc_auc_score(true_labels, resulting_values)
score_2 = roc_auc_score(true_labels, -resulting_values)
print("> Final score:", max(score_1, score_2))

print("> Plotting ROC curve")
if score_1 > score_2:
    RocCurveDisplay.from_predictions(true_labels, resulting_values)
else:
    RocCurveDisplay.from_predictions(true_labels, -resulting_values)
plt.show()
