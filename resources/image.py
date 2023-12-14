from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from config import Config
from mysql_connection import get_connection
from mysql.connector import Error

from datetime import datetime

import boto3


class FileUploadResource(Resource):
    def post(self):

        file = request.files.get('photo')

        if file is None :
            return {'error':'파일을 업로드 하세요'}, 400
        
        # 파일명을 회사의 파일명 정책에 맞게 변경한다.
        # 파일명은 유니크 해야한다.
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'
        
        # 유저가 올린 파일의 이름을 새로운 파일 이름으로 변경한다.
        file.filename = new_file_name

        # S3 스토리지에 업로드 하면 된다.
        # AWS에서 제공하는 파이썬 라이브러리인 boto3 라이브러리를 이용해야한다.
        # boto3 라이브러리는 AWS의 모든 서비스를 파이썬 코드로 작성할 수 있는 라이브러리이다.
        # 로컬에 이 라이브러리 설치한적 없으므로 pip install boto3
        s3 = boto3.client('s3', 
                     aws_access_key_id = Config.AWS_ACCESS_KEY,
                     aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)

        try :
            s3.upload_fileobj(file, Config.S3_BUCKET, 
                              file.filename, 
                              ExtraArgs = {'ACL':'public-read', 
                                           'ContentType':'image/jpeg'})
        
        except Exception as e:
            print(e)
            return {'error': str(e)}, 500
        
        
        return {"result":"success",
                "imgUrl":Config.S3_LOCATION + file.filename}, 200


