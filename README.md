# s3-bouncer

![s3-bouncer](https://raw.githubusercontent.com/ezyang/s3-bouncer/master/s3-bouncer.png)

This small web app issues pre-signed URLs to an S3 bucket.  You might
want this if you need an S3 bucket that allows public writes and reads,
but within some limits... and you don't want to just publish IAM
credentials of a user.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
