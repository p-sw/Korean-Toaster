# Korean Toaster

## 프로젝트 개요

Korean Toaster는 Windows 환경에서 한국어 입력 상태를 시각적으로 표시해주는 데스크톱 애플리케이션입니다. 사용자가 Alt 키나 한/영 키를 누를 때 현재 입력 모드(한국어 "가" 또는 영어 "A")를 화면에 팝업으로 보여줍니다. 이를 통해 사용자는 현재 입력 언어 상태를 한눈에 확인할 수 있습니다.

## 프로젝트 언어, 의존성, 프레임워크

### 주요 언어

- **Python 3.x**: 메인 애플리케이션 언어
- **JavaScript**: 빌드 및 개발 스크립트 관리 (package.json)

### Python 의존성

- `keyboard==0.13.5`: 키보드 이벤트 감지 및 후킹
- `Pillow==11.2.1`: 이미지 처리 (트레이 아이콘용)
- `pystray==0.19.5`: 시스템 트레이 인터페이스
- `pyglet==2.1.6`: UI 렌더링 및 폰트 관리

### 프레임워크 및 라이브러리

- **Tkinter**: GUI 팝업 창 구현
- **Windows API (ctypes)**: IME 상태 감지 및 모니터 정보 획득
- **PyInstaller**: 실행 파일 빌드

## 프로젝트 구조

```
Korean-Toaster/
├── main.py                    # 애플리케이션 진입점
├── package.json               # 빌드 스크립트 및 의존성 관리
├── requirements.txt           # Python 의존성
├── icon.ico                   # 애플리케이션 아이콘
├── LICENSE                    # 라이센스 파일
├── yarn.lock                  # JavaScript 의존성 락 파일
├── _internal/
│   └── resources/
│       ├── icon.png           # 트레이 아이콘
│       └── Pretendard-Regular.otf  # UI 폰트
└── src/
    ├── conf.py                # 설정 관리 (JSON 기반)
    ├── constants.py           # 상수 정의
    ├── cpp.py                 # Windows API 래퍼 및 언어 감지
    ├── logger.py              # 로깅 시스템
    ├── monitor.py             # 키보드 이벤트 모니터링
    ├── tray.py                # 시스템 트레이 관리
    ├── ui.py                  # GUI 팝업 인터페이스
    └── utils.py               # 유틸리티 함수
```

### 주요 모듈별 역할

- **main.py**: `AppConductor` 클래스를 통해 전체 애플리케이션 오케스트레이션
- **src/cpp.py**: Windows IME API를 통한 한국어/영어 입력 상태 감지
- **src/ui.py**: 둥근 모서리 팝업 창과 페이드 애니메이션 구현
- **src/tray.py**: 시스템 트레이 메뉴를 통한 설정 인터페이스 제공
- **src/monitor.py**: 키보드 후킹을 통한 Alt/한영 키 감지
- **src/conf.py**: JSON 기반 설정 관리 및 실시간 변경 감지

## 프로젝트 워크플로우

### 1. 애플리케이션 초기화

```
main.py → AppConductor 생성
├── Configuration 로드 (config.json)
├── LanguageDetector 초기화 (Windows IME API)
├── AppUI 생성 (Tkinter 팝업 창)
├── AppTray 생성 (시스템 트레이)
└── KeyboardMonitor 생성 (키보드 후킹)
```

### 2. 키 이벤트 처리 플로우

```
사용자가 Alt/한영 키 누름
↓
KeyboardMonitor가 이벤트 감지
↓
AppConductor.hangeul_handler 호출
├── 설정에 따른 키 필터링 (좌Alt/우Alt 무시 옵션)
├── IME 상태 업데이트 대기 (0.05초 지연)
├── LanguageDetector.update() 실행
│   └── Windows SendMessage API로 변환 모드 확인
├── 현재 언어 상태 판별 ("가" 또는 "A")
└── AppUI.show_popup() 호출
    ├── 모니터 설정에 따른 창 위치 계산
    ├── 팝업 창 표시 (알파값 1.0)
    ├── 설정된 시간 후 페이드아웃 시작
    └── 애니메이션 완료 후 창 숨김
```

### 3. 설정 관리 플로우

```
사용자가 트레이 아이콘 우클릭
↓
AppTray 메뉴 표시
├── 창 유지 시간 설정 (0초~3초)
├── 애니메이션 속도 설정 (끄기~3초)
├── 창 크기 설정 (1/4, 1/6, 1/8)
├── 다중 모니터 설정
│   ├── 항상 주 모니터
│   ├── 커서가 있는 모니터
│   └── 활성 윈도우가 있는 모니터
└── 설정 변경 시 즉시 config.json 저장
```

### 4. 빌드 및 배포

```bash
# 개발 환경 설정
yarn setup  # pip install -r requirements.txt

# 개발 모드 실행
yarn dev    # py main.py

# 프로덕션 빌드
yarn build  # pyinstaller를 통한 실행 파일 생성
```

이 프로젝트는 Windows 사용자의 한국어 입력 환경을 개선하기 위한 유틸리티로, 특히 한영 전환 상태를 명확하게 파악할 수 있도록 도와주는 도구입니다.
