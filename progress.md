## 2023.05.09

### Fault Localization (김윤호 교수님)
- 현재 진행된 내용: 
Python 프로그램을 대상으로 코드 커버리지 스펙트럼 기반 알고리즘 구현 (Tarantula, Ochiai, Op2 D* 4개 구현)
Gcov 커버리지 결과를 CSV 로 변환하기 위한 변환 모듈 개발

- 앞으로 진행할 부분: 
파이썬 코드 커버리지 결과를 CSV 로 변환하기 위한 변환 모듈 개발
프레임워크 입출력에 맞추고 끼워넣기 위한 구현 

### Hot Patching (이주용 교수님)
- 런타임복구에대한계획수립: (1) 에러인지-> (2) 시스템정지-> (3) 에러발생전으로프로그램상태  복구-> (4) 패치탐색및검증-> (5) 사용자에게패치옵션제시
- 현재예외상황에러에대한시스템정지까지개발되었으며복구부분작업중

### Patch Generation (김동선 교수님)
- 현재 두가지 patch generation 기술을 검증 중: neural patch generation 과 pattern-based patch generation.
- Neural patch generation 기술을 우리 프레임워크에 적용 가능한지 테스트 중.
- Python언어를 위한 fix pattern 수집 중.

### Patch Validation (오학주 교수님)
- 프레임워크 프로토타입 개발
- 오답 패치 특성 추출기 개발
