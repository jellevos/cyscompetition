In collaboration with WIFS, TU Delft CYS is organizing a competition in the domain of signal processing, combining biometrics and secure computation. Specifically, competitors are tasked to create a **private odor-based access control system** that matches encrypted human samples with permitted encrypted samples on an external database. The sensitive nature of the biometric samples requires them to be encrypted both at rest and in transit. At the same time, to prevent long waiting times, the access control mechanism is supposed to answer queries within only a second.

[Register here!]()

## Story
For years now, company A has used a very traditional form of access control: They had dogs sniff each passerby, barking if the dog recognized them. This worked great when the company had 10 employees, but things became harder for a 100; while the dogs certainly enjoyed the increased attention, they certainly took longer to bark. Now, the company has reached 1000 employees, and the dogs are having a hard time keeping track of all the different odors. So, in 2022, this company is going high-tech! E-noses replace the dogs, who from now on get to take pets for free.

The access control system based on e-noses is provided by company B, which also serves many other clients. Since they are storing a significant amount of sensitive biometric data, they promise that all data, both at rest and in transit, is encrypted.

## Data
For this competition, all data is artificially generated to resemble 'human' odors measured using [gas chromatography](https://en.wikipedia.org/wiki/Gas_chromatography). Note that **we do not offer any guarantees about how realistic these samples are**, although we certainly try to.
> We will add more details about the data that is given to the participants at a later time.

## Objective
The primary objective is to **maximize** the area-under-curve of the receiver operating curve (**ROC-AUC**) of the binary classification (access denied / access granted). This is the metric we use to decide the winners. In the case of a tie (up to 3 places behind the comma), we look at the run time. There are several constraints:

- The total run time for a query must take less than one second, otherwise, it is counted as incorrect. *We set a specific bandwidth so you can calculate the time it costs to transmit.*
- The server must not be able to learn any information from the input it receives. *In other words, the input to the server must be computationally indistinguishable from any other input.*
- Each e-nose has a distinct key, with which all its queries are encrypted. *In other words, an e-nose cannot decrypt another e-nose’s images.*
- Each query has only one interaction: The e-nose queries the server, and the server sends one response.

The server is expected to return a value that the client will interpret as ‘true’ if it is above a certain threshold, and ‘false’ if it is below. To compute the ROC-AUC we will vary this threshold so whether these values lie between 0-1 or any other range is not important.

## Evaluation

The server will be populated with a database of 1000 people’s odor measurements. During the evaluation, each one of the three e-noses will send 500 queries of faces to the server. All solutions will be evaluated on the same data.

## Baseline solution
> We will provide a baseline solution based on PCA and a simple homomorphic circuit.

## Prizes
1st place: 500 euros

2nd place: 250 euros

3rd place: 125 euros

> Prizes are not yet final.

## Timeline
1st of July: Kickoff

1st of October: Deadline

> We will provide more details later.

## Submitting
> We will include details on the submission format, deadlines and a submitting form at a later time.

## Frequently-asked questions
*We will update this section based on the questions we receive. Please find our contact details below.*

## Contacts
This competition is organized by the CYS group of Delft University of Technology.
Please feel free to contact us at cyscompetition@tudelft.nl with questions regarding this competition.
