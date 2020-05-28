# musaic

## Architectural Overview
Musaic is comprised of several different services that work in tandem to deliver the final musaic.

### Web App
The Musaic web app is a node.js + express app that serves Pug views. It is deployed
on a free tier of heroku.

### S3
Uploaded photos and generated photos (musaics) are stored in S3. All keys in S3 have an expiration
date of one day after initial creation. This means that we don't store your photos for more than 24 hours.

### Step Functions
AWS Step Functions are used to initiate the creation of the musaic and monitor the status of execution.
Because the generation of the musaic takes a non-trivial amount of time, we do it asynchronously and poll
the step function for the completion status.

### Lambda
The algorithm that generates the musaic is adapted from [https://github.com/codebox/mosaic]. In particular,
it is adapted to run in an AWS lambda environment by using the python multiprocessing library's Pipe capabilities.
When a user confirms the playlist they want to use, a Step Function is triggerd which
initiates a lambda function that pulls the appropriate uploaded photo from S3, downloads the playlist's album covers,
generates the musaic, and stores it back in S3. 

