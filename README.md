codeGPT-FastAPI
========
- wiki 및 코드 설명
- requirements 설명


## Dockerfile
## Anaconda
## FastAPI

## **requirements.txt**
fastapi==0.78.0
protobuf==3.20.0
pydantic==1.9.1
python-multipart==0.0.5
transformers==4.20.1
uvicorn==0.18.2

## **config.py**
- 자료형과 Default값을 수정할 수 있습니다.
- API request form과 response form은 dict형식입니다.

## **model.py**
- 모델에 값을 입력해서 결과를 받아줍니다.
- 반복문을 통해서 요청이 들어왔는지 확인합니다.
- 요청이 있다면 코드가 실행됩니다.
- `Request`에 `output`을 추가해주고, dict형태로 `result`에 결과를 담아 반환합니다.
- `exception`이 발생하면, `result`대신 `error`에 `Exception`내용을 담아 반환합니다.


## **main.py**
- model thread를 만들어서 서버와 별개로 요청을 받을 수 있게 해줍니다.
- 문제 없이 진행되면 `APIResponse`형식으로 반환합니다.
- 문제가 발생하면 `HTTPException`형식으로 반환합니다.


## Reference
- [FastAPI Docs](https://fastapi.tiangolo.com/ko/)
