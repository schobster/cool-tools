# Overview
This tool can be used to bulk-modify the keys in an AWS S3 bucket.

# How to Use
In order to make the tool update keys in the way you need, you must define two 
functions in your version of the python script:
1) A function which evaluates a key(string) and returns True if the key needs to be updated. 
    If you want to update every single key in a bucket, just write a stub function which returns True.
    
2) A function which accepts the current string value of the key, and returns the new key. 

You must also set the S3_BUCKET global to the name of the S3 bucket you would like to update.

Last but not least, update the last line of this script to pass in the two functions you have created above.

Once that's all set, just run the script, sit back, and watch the glory of S3 objects being renamed.

# Troubleshooting
Ensure you have CLI access to your S3 bucket via boto3/AWS SDK. boto3 checks for AWS credentials in
the following manner: http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials
