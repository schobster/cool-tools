"""
This script can be used to bulk-modify the keys in an AWS S3 bucket.

In order to make the script update keys in the way you need, you must define two 
functions in your version of this script:
1) A function which evaluates a key and returns True if the key needs to be updated. 
    If you want to update every single key in a bucket, just write a stub function which returns True.
    (example: month_year_is_5_chars)
2) A function which accepts the current string value of the key, and returns the new key. 
    (example: prepend_month_with_zero)

You must also set the S3_BUCKET global to the name of the S3 bucket you would like to update.

Last but not least, update the last line of this script to pass in the two functions you have created above,
rather than re-use the example functions.

Once that's all set, just run the script, sit back, and watch the glory of S3 objects being renamed.

Troubleshooting:
Ensure you have CLI access to your S3 bucket via boto3/AWS SDK. boto3 checks for AWS credentials in
the following manner: http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials
"""
import boto3
import logging

S3_BUCKET = ''
S3_CLIENT = boto3.client('s3')
LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.addHandler(logging.FileHandler("s3_update.log"))


def bulk_update_key_names(needs_update, generate_new_key):
    """
    Iterate through all keys in an s3 bucket, evaluate each for whether it should be updated, then perform the update.
    :param needs_update: a function returning a Boolean value indicating whether or not a key needs to be updated 
    :param generate_new_key: a function which takes in an existing key and returns the desired new key.
    """
    keys = get_keys_in_bucket()
    for key in keys:
        if needs_update(key):
            new_key = generate_new_key(key)
            update_key_in_s3(key, new_key)


def get_keys_in_bucket():
    """
    Retrieves a list of the keys in the s3 bucket
    :return list<string>: A list of all keys currently in the bucket.  
    """
    bucket = boto3.resource('s3').Bucket(S3_BUCKET)
    objects = bucket.objects.all()
    keys = []
    for s3obj in objects:
        keys.append(s3obj.key)
    return keys


def update_key_in_s3(old_key, new_key):
    """
    Copies the existing S3 object, giving it the new key, then deletes the pre-existing S3 object with the
    undesired key.
    :param old_key: the key of the existing S3 object 
    :param new_key: the key to replace it with
    """
    LOGGER.info("Attempting to replace " + old_key + " with " + new_key)

    # Copy the existing s3 object, giving it the new key
    S3_CLIENT.copy_object(
        Bucket=S3_BUCKET,
        CopySource={
            'Bucket': S3_BUCKET,
            'Key': old_key
        },
        Key=new_key
    )

    # Delete the old s3 object.
    S3_CLIENT.delete_object(
        Bucket=S3_BUCKET,
        Key=old_key
    )

    LOGGER.info("Successfully replaced " + old_key + " with " + new_key)


"""
Example functions for needs_update and generate_new_key, respectively. 
In the use case this script was created for, we had keys with a year and month in them, 
and for single-digit months we needed to add a 0 in, 
Example: change 20111 to 201101 for Jan of 2011
"""


def month_year_is_5_chars(key):
    """
    Checks if the year-month piece of our key is 5 chars long, indicating it needs updating.
    """
    month_year = key.split('.')[1]  # Key is of the form <weather var>.<yearmonth>.grib2, so grab the middle piece
    if len(month_year) == 5:  # A reliable check for whether the key is YYYYM or YYYYMM.
        return True
    else:
        return False


def prepend_month_with_zero(old_key):
    """
    Inserts a 0 into the year-month piece of our key.
    """
    split_key = old_key.split('.')
    yearmonth = split_key[1]
    yearmonth = yearmonth[:4] + '0' + yearmonth[4]
    new_key = split_key[0] + '.' + yearmonth + '.' + split_key[2]
    return new_key


if __name__ == '__main__':
    bulk_update_key_names(month_year_is_5_chars, prepend_month_with_zero)
