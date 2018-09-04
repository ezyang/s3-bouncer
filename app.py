import os
from flask import Flask, request
import boto3
import uuid
import dns.resolver
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

@app.route('/')
def main():
    return 'POST to /put or /get'

@app.route('/put', methods=['POST'])
def put():
    dns_whitelist = os.getenv("S3_BOUNCER_DNS_WHITELIST")
    if dns_whitelist is not None:
        print("Visitor is:", request.remote_addr)
        for rdata in dns.resolver.query(dns_whitelist, 'A'):
            print("Checking against:", rdata)
            if request.remote_addr == str(rdata):
                break
        else:
            return "not authorized"
    s3 = boto3.client('s3')
    obj = str(uuid.uuid4())
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': os.getenv("S3_BOUNCER_BUCKET"),
            'Key': obj
        },
        ExpiresIn=100
    )
    return url

@app.route('/get/<obj>', methods=['POST'])
def get(obj):
    s3 = boto3.client('s3')
    def set_accessed_tag(v):
        s3.put_object_tagging(
                Bucket=os.getenv("S3_BOUNCER_BUCKET"),
                Key=obj,
                Tagging={
                        'TagSet': [
                            {'Key': 'Accessed', 'Value': v}
                            ]
                    }
                )
    obj_tags = s3.get_object_tagging(Bucket=os.getenv("S3_BOUNCER_BUCKET"), Key=obj)
    for kv in obj_tags["TagSet"]:
        if kv['Key'] == 'Accessed':
            if kv['Value'] == '1':
                set_accessed_tag('2')
                break
            else:
                return "object has already been accessed twice", 403
    else:
        set_accessed_tag('1')
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': os.getenv("S3_BOUNCER_BUCKET"),
            'Key': obj
        },
        ExpiresIn=100
    )
    return url

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
