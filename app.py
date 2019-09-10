from flask import Flask, render_template, request

import json, boto3
from boto3.dynamodb.conditions import Key
from credentials import dynamo_aws_id_key, dynamo_aws_secret_key


def login(username,password):
    session = boto3.Session( aws_access_key_id=dynamo_aws_id_key, aws_secret_access_key=dynamo_aws_secret_key)
    db = session.resource('dynamodb',region_name = "us-east-1",aws_session_token=None)
    tab = db.Table('finance-login')
    resp = tab.get_item(Key={"username": username})
    print("Tentativa de Login com Resposta:" + str(resp['ResponseMetadata']['HTTPStatusCode']))
    if resp['Item']['password'] == password and resp['Item']['username'] == username:
        print("-- Success Loggin!")
        return True
    else:
        print("-- Unhappy Loggin ")
        return False


app = Flask(__name__)

@app.route("/",methods = ['POST'])
def main():
    if not login( str(request.form.get('username')) , str(request.form.get('password')) ):
        return "Credenciais incorretas!!"
    else:
        session = boto3.Session( aws_access_key_id=dynamo_aws_id_key, aws_secret_access_key=dynamo_aws_secret_key)
        Pay = '{"month":'+request.form.get('month')+',"year":'+request.form.get('year')+'}'
        client = session.client('lambda')
        response = client.invoke(
            FunctionName='SUMMARY-GENERATE',
            InvocationType='RequestResponse',
            Payload=bytes(Pay, 'utf-8'),
        )
        byteResponse = response['Payload'].read().decode('utf-8')
        return json.loads(json.loads(byteResponse)['body'])['message'] #summ(int(request.form.get('month')) , int(request.form.get('year')) )
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
