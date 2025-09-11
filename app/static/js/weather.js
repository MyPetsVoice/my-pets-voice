class WeatherWidget {
  constructor(containerId, location = "서울") {
    this.container = document.getElementById(containerId);
    this.location = location;
    this.locations = []; // 지원 지역 목록
    this.widgetId = containerId; // 위젯 고유 ID 저장 (ID 충돌 방지용)

    if (!this.container) {
      console.error(`날씨 위젯 컨테이너 '${containerId}'를 찾을 수 없습니다.`);
      return;
    }

    this.init();
  }

  // 위젯 초기화
  init() {
    this.loadLocations(); // 지역 목록 먼저 로드
    this.render(); // HTML 구조 생성
    this.loadWeatherData(); // 날씨 데이터 로드
  }

  // 지원 지역 목록 로드
  loadLocations() {
    fetch("/api/weather/locations")
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          this.locations = data.locations;
          this.updateLocationSelector();
        }
      })
      .catch((error) => {
        console.error("지역 목록 로드 실패:", error);
      });
  }

  // 위젯 HTML 구조 생성 (가로 배치) - ID 충돌 방지를 위해 고유 ID 사용
  render() {
    const isMobile = this.container.id === "mobile-weather";

    this.container.innerHTML = `
            <div class="weather-widget">
                <div class="flex items-center ${
                  isMobile ? "space-x-1" : "space-x-3"
                }">
                    <!-- 지역 선택 드롭다운 (모바일에서는 숨김) -->
                    <div class="flex-shrink-0 ${isMobile ? "hidden" : ""}">
                        <select id="locationSelect-${
                          this.widgetId
                        }" class="bg-gray-100 text-gray-700 text-sm rounded px-2 py-1 border border-gray-200 focus:outline-none focus:border-primary-300 focus:bg-white min-w-16">
                            <option value="${this.location}">${
      this.location
    }</option>
                        </select>
                    </div>
                    
                    <!-- 날씨 정보 -->
                    <div class="flex items-center ${
                      isMobile ? "space-x-1" : "space-x-2"
                    }">
                        <div id="weatherIcon-${this.widgetId}" class="${
      isMobile ? "text-sm" : "text-2xl"
    }">⏳</div>
                        <div class="text-center">
                            <div id="currentTemp-${this.widgetId}" class="${
      isMobile
        ? "text-sm font-medium text-gray-600"
        : "text-lg font-medium text-gray-700"
    }">--°</div>
                            ${
                              isMobile
                                ? ""
                                : `<div id="weatherText-${this.widgetId}" class="text-xs text-gray-500 whitespace-nowrap">로딩중...</div>`
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;

    this.setupEventListeners();
  }

  // 이벤트 리스너 설정 - 고유 ID 사용
  setupEventListeners() {
    const locationSelect = document.getElementById(
      `locationSelect-${this.widgetId}`
    );
    if (locationSelect) {
      locationSelect.addEventListener("change", (e) => {
        this.setLocation(e.target.value);
      });
    }
  }

  // 지역 선택 드롭다운 옵션 업데이트 - 고유 ID 사용
  updateLocationSelector() {
    const locationSelect = document.getElementById(
      `locationSelect-${this.widgetId}`
    );
    if (locationSelect && this.locations.length > 0) {
      locationSelect.innerHTML = this.locations
        .map(
          (location) =>
            `<option value="${location}" ${
              location === this.location ? "selected" : ""
            }>${location}</option>`
        )
        .join("");
    }
  }

  // 로딩 상태 표시 - 고유 ID 사용하여 요소에 안전하게 접근
  loadWeatherData() {
    // 각 위젯별 고유 ID로 요소를 찾아서 안전하게 업데이트
    const tempElement = document.getElementById(`currentTemp-${this.widgetId}`);
    const iconElement = document.getElementById(`weatherIcon-${this.widgetId}`);
    const textElement = document.getElementById(`weatherText-${this.widgetId}`);

    // 요소가 존재하는 경우에만 업데이트 (안전장치)
    if (tempElement) tempElement.textContent = "--°";
    if (iconElement) iconElement.textContent = "⏳";
    if (textElement) textElement.textContent = "로딩중..."; // 모바일에서는 이 요소가 없을 수 있음

    // 위젯용 API 호출
    fetch(`/api/weather/widget?location=${encodeURIComponent(this.location)}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          this.updateDisplay(data);
        } else {
          console.error("날씨 데이터 로드 실패:", data.message);
          this.showError();
        }
      })
      .catch((error) => {
        console.error("날씨 API 호출 오류:", error);
        this.showError();
      });
  }

  // 화면에 날씨 정보 표시 - 고유 ID 사용하여 각 위젯별로 안전하게 업데이트
  updateDisplay(weatherData) {
    // 각 위젯별 고유 ID로 요소를 찾아서 업데이트
    const tempElement = document.getElementById(`currentTemp-${this.widgetId}`);
    const iconElement = document.getElementById(`weatherIcon-${this.widgetId}`);
    const textElement = document.getElementById(`weatherText-${this.widgetId}`);

    // 요소가 존재하는 경우에만 업데이트
    if (tempElement) {
      tempElement.textContent = `${weatherData.temperature}°`;
    }
    if (iconElement) {
      iconElement.textContent = weatherData.weather_emoji;
    }
    if (textElement) {
      textElement.textContent = weatherData.weather_text;
    }
  }

  // 오류 상태 표시 - 고유 ID 사용하여 안전하게 처리
  showError() {
    const tempElement = document.getElementById(`currentTemp-${this.widgetId}`);
    const iconElement = document.getElementById(`weatherIcon-${this.widgetId}`);
    const textElement = document.getElementById(`weatherText-${this.widgetId}`);

    // 요소가 존재하는 경우에만 오류 상태 표시
    if (tempElement) tempElement.textContent = "--°";
    if (iconElement) iconElement.textContent = "⚠️";
    if (textElement) textElement.textContent = "정보 없음";
  }

  // 지역 변경
  setLocation(newLocation) {
    this.location = newLocation;
    this.loadWeatherData();
  }
}

// 위젯 초기화 함수
function initWeatherWidget(containerId, location = "서울") {
  return new WeatherWidget(containerId, location);
}
