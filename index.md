In collaboration with [WIFS](https://wifs2022.utt.fr/), TU Delft CYS is organizing a competition in the domain of signal processing, combining biometrics and secure computation. Specifically, competitors are tasked to create a **private odor-based access control system** that matches encrypted human samples with permitted encrypted samples on an external database. The sensitive nature of the biometric samples requires them to be encrypted both at rest and in transit. At the same time, to prevent long waiting times, the access control mechanism is supposed to answer queries within only a second.

[Register here!](https://forms.office.com/Pages/ResponsePage.aspx?id=TVJuCSlpMECM04q0LeCIezoA7-5OJkxKgUWsouHTGZtUNzJJNlVCQ1VHNVA0UU9FQVJDSUgwU0xRSy4u)

## Story
For years now, company A has used a very traditional form of access control: They had dogs sniff each passerby, barking if the dog recognized them. This worked great when the company had 10 employees, but things became harder for a 100; while the dogs certainly enjoyed the increased attention, they certainly took longer to bark. Now, the company has reached 1000 employees, and the dogs are having a hard time keeping track of all the different odors. So, in 2022, this company is going high-tech! E-noses replace the dogs, who from now on get to take pets for free.

The access control system based on e-noses is provided by company B, which also serves many other clients. Since they are storing a significant amount of sensitive biometric data, they promise that all data, both at rest and in transit, is encrypted.

## Objective
The primary objective is to **maximize** the area-under-curve of the receiver operating curve (**ROC-AUC**) of the binary classification (access denied / access granted). This is the metric we use to decide the winners. In the case of a tie (up to 3 places behind the comma), we look at the run time. There are several constraints:

- The total run time for a query must take less than one second, otherwise, it is counted as incorrect. *We set a specific bandwidth so you can calculate the time it costs to transmit.*
- The server must not be able to learn any information from the input it receives. *In other words, the input to the server must be computationally indistinguishable from any other input.*
- Each e-nose has a distinct key, with which all its queries are encrypted. *In other words, an e-nose cannot decrypt another e-nose’s images.*
- Each query has only one interaction: The e-nose queries the server, and the server sends one response.
- The cryptographic parameters satisfy at least _128 bits of security_ ([see the homomorphic encryption standard](https://homomorphicencryption.org/standard/)).

The server is expected to return a value that the client will interpret as ‘true’ if it is above a certain threshold, and ‘false’ if it is below. To compute the ROC-AUC we will vary this threshold so whether these values lie between 0-1 or any other range is not important.

## Evaluation
The server will be populated with a database of 1000 people’s odor measurements. During the evaluation, each one of the three e-noses will send 500 queries of _encrypted_ odor measurements and their _supposed_ user id to the server. All solutions will be evaluated on the same data.

## Data & baseline solution
For this competition, all data is artificially generated to resemble 'human' odors measured using [gas chromatography](https://en.wikipedia.org/wiki/Gas_chromatography). Note that **we do not offer any guarantees about how realistic these samples are**, although we certainly try to.
> We will add the data & a baseline for participants on the 8th of July.

## Prizes
1st place: 500 euros  
2nd place: 250 euros  
3rd place: 125 euros  

## Timeline
**1st of July:** Kickoff!  
**8th of July:** Data & baseline online.  
**1st of September:** Submission system opens.  
**1st of October:** Submission deadline & [early registration deadline for WIFS](https://wifs2022.utt.fr/registration).  
**12th-16th of December:** Results announced at WIFS.  

## Submitting
> We will include details on the submission format, deadlines and a submitting form at a later time.

## Frequently-asked questions
**Why are you targeting odors as a biometric?**  
It was not an option for us to generate a new real-life dataset, so we had to resort to generating artificial data. For biometrics like fingerprints, faces, and iris scans, there are public generators available. To level the playing field we decided to create a new data generation pipeline for another biometric, and to keep it hidden until the results are announced.

**Will the winning teams have their work published?**  
The competition ends after the submission deadline for WIFS, but we encourage (and will work together with) the winning teams to summarize their work in a submission to [IEEE T-IFS](https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=10206).

**Can our institution register multiple teams?**  
Yes! The only rule we enforce here is that each person only takes part in one team.

## Contacts
This competition is organized by the CYS group of Delft University of Technology.
Please feel free to contact us at [cyscompetition@tudelft.nl](mailto:cyscompetition@tudelft.nl) with questions regarding this competition.
