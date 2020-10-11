# SSD37 - Data Storage and Interface for Processing

## Team members

| Name            | Roll No.   | Github ID                  |
|-----------------|------------|----------------------------|
| Rani Tresa Gigi | 2020202019 | github.com/ranitresa98     |
| Ronit Ray       | 2020201024 | github.com/ronitray95      |
| Akashdeep Singh | 2020201051 | github.com/Akashdeepsingh98|

<br/>
<br/>

## Our understanding of project

- We believe that we need to take as input a bunch of bibtex and constraints.
- We need to store this provided data on the server.
- The output of the project should be the bibtex and papers which match the provided filters, in a specified format.
- The output should have papers ranked according to some quality assessment.
- We can design the UI as we see fit.
- The technologies we can use consist of the Javascript and Python ecosystems.

## Approach

- Our approach will be linear towards building the project.
- We will be designing the API that can accept the bibtex in whichever format that is needed - CSV and JSON first.
- Then store the provided data in a NoSQL database which can be either on-premise (MongoDB) or cloud-based (MongoDB / Firebase Realtime Database).
- This allows for more flexible indexing than SQL databases and will help us in filtering out data.
- We will be applying the constraints provided.
- Quality assessment techniques for ranking the papers will be implemented next - better papers are higher.
- The final output of the process will be given to the user in one coherent piece in a specified format.

## Relevant Study Material

## Milestones for us

1. Developing the front end API for user.
2. Parsing through the data and organzing all of it in storage.
3. Performing quality assessment.
4. Giving the output to the user.
