codeGPT-FastAPI
========

## Dockerfile
- [dockerhub](https://hub.docker.com/)에 있는 [pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime](https://hub.docker.com/layers/pytorch/pytorch/pytorch/1.9.0-cuda11.1-cudnn8-runtime/images/sha256-e04020e1b6cc744659c70f5afdc0ab602486f24d74f9ba44929c14b7442dca31?context=explore) 이미지 사용
- `FROM`: 존재하는 이미지 가져오기(Dockerhub참고)
- `WORKDIR`: 디렉터리 이동
- `COPY`: copy `src` `dest` : host의 파일(src)을 이미지 안(dest)으로 복사
- `EXPOSE`: 네트워크 포트와 프로토콜 지정용 명령어
- `RUN`: 이미지 **빌드** 시 커맨드를 실행한다
- `CMD`: 이미지 **실행** 시 커맨드를 실행한다

## [Anaconda](https://www.anaconda.com/)
- 버전 관리와 패키지 관리용
- `ANACONDA.NAVIGATOR`로 GUI환경에서 볼 수 있음
- 환경이 activate된 상태에서 `pip`를 써도 그 환경에만 적용됨

### **Conda 명령어**
- 설치 후 `conda -V`로 확인
- 가상환경 만들기: `conda create -n {env_name} python={version}`
- 가상환경 삭제: `conda remove -n {env_name} --all`
- 가상환경 리스트 확인: `conda env list`
- 가상환경 실행: `source activate {env_name}` or `conda activate {env_name}`
- 가상환경 종료: `deactivate`
- 설치된 패키지 확인: `conda list`
- 패키지 설치: `conda install {package_name}`
  - 다만, `requirements.txt`를 만들 예정이라면 `pip`로 설치하는 것을 권장한다.
  - conda를 쓸 것이라면 되도록 conda로만 설치해서 dockerize할 때 잘 설정해줘야 한다.
  - `conda list -e > requirements.txt`로 requirements.txt를 만들 수 있다.
  - `conda env export > requirements.txt`가 더 예쁘게 나온다.
  - `-e, --export`옵션은 requirement string만 출력한다.
  - 그리고 결과값을 `conda create --file {file_name}`명령어에 의해 사용될 수 있게 해준다.
- 패키지 삭제: `conda remove {package_name}`

### **pip 명령어**
- 설치된 패키지 확인: `pip freeze`
  - `pip freeze > requirements.txt`로 `requirements.txt`로 저장 가능하다.
  - `pip install -r requirements.txt`로 설치한다.
- 패키지 설치: `pip install {package_name}`
- 패키지 삭제: `pip uninstall {package_name}`

## FastAPI
- `HTTPException`: 파이썬 exception에 api와 관련된 데이터를 추가한 exception
  - `raise`를 활용하고 `status_code`와 `detail`을 적절히 입력한다.
- `python`의 특징을 잘 활용해야함. 
  - annotation: type 명시하기
  - `def generate(request: APIRequest)->APIResponse` 에서
  - `: APIRequest`와 `->APIResponse`부분. python은 type이 없어도 원래 실행됨
  - docstring: 일종의 주석처리. 함수가 호출되면 이 주석 출력
  - 함수에 대한 이해를 증진시킴
- `Reference`에 있는 튜토리얼을 꼭 참고하기

## **requirements.txt**
- `fastapi==0.78.0`: FastAPI
- `pydantic==1.9.1`: FastAPI에서 `BaseModel`을 사용하기 위함
- `transformers==4.20.1`: Docker image에 포함되어 있지 않은 것 같다. 없으면 오류 발생
- `uvicorn==0.18.2`: ASGI web server
  - 비동기 처리가 가능한 웹 서버 인터페이스


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
