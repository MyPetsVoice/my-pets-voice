class WeatherWidget {
  constructor(containerId, location = "서울") {
    this.container = document.getElementById(containerId);
    this.location = location;
    this.locations = []; // 지원 지역 목록

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

  // 위젯 HTML 구조 생성 (가로 배치)
  render() {
    const isMobile = this.container.id === 'mobile-weather';
    
    this.container.innerHTML = `
            <div class="weather-widget">
                <div class="flex items-center ${isMobile ? 'space-x-1' : 'space-x-3'}">
                    <!-- 지역 선택 드롭다운 (모바일에서는 숨김) -->
                    <div class="flex-shrink-0 ${isMobile ? 'hidden' : ''}">
                        <select id="locationSelect" class="bg-gray-100 text-gray-700 text-sm rounded px-2 py-1 border border-gray-200 focus:outline-none focus:border-primary-300 focus:bg-white min-w-16">
                            <option value="${this.location}">${this.location}</option>
                        </select>
                    </div>
                    
                    <!-- 날씨 정보 -->
                    <div class="flex items-center ${isMobile ? 'space-x-1' : 'space-x-2'}">
                        <div id="weatherIcon" class="${isMobile ? 'text-sm' : 'text-2xl'}">⏳</div>
                        <div class="text-center">
                            <div id="currentTemp" class="${isMobile ? 'text-sm font-medium text-gray-600' : 'text-lg font-medium text-gray-700'}">--°</div>
                            ${isMobile ? '' : '<div id="weatherText" class="text-xs text-gray-500 whitespace-nowrap">로딩중...</div>'}
                        </div>
                    </div>
                </div>
            </div>
        `;

    this.setupEventListeners();
  }

  setupEventListeners() {
    const locationSelect = document.getElementById("locationSelect");
    if (locationSelect) {
      locationSelect.addEventListener("change", (e) => {
        this.setLocation(e.target.value);
      });
    }
  }

  // 지역 선택 드롭다운 옵션 업데이트
  updateLocationSelector() {
    const locationSelect = document.getElementById("locationSelect");
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

  // 로딩 상태 표시
  loadWeatherData() {
    document.getElementById("currentTemp").textContent = "--°";
    document.getElementById("weatherIcon").textContent = "⏳";
    document.getElementById("weatherText").textContent = "로딩중...";

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

  // 화면에 날씨 정보 표시
  updateDisplay(weatherData) {
    document.getElementById(
      "currentTemp"
    ).textContent = `${weatherData.temperature}°`;
    document.getElementById("weatherIcon").textContent =
      weatherData.weather_emoji;
    document.getElementById("weatherText").textContent =
      weatherData.weather_text;
  }

  showError() {
    document.getElementById("currentTemp").textContent = "--°";
    document.getElementById("weatherIcon").textContent = "⚠️";
    document.getElementById("weatherText").textContent = "정보 없음";
  }

  // 지역 변경
  setLocation(newLocation) {
    this.location = newLocation;
    this.loadWeatherData();
  }
}

// 위젯 초기화
function initWeatherWidget(containerId, location = "서울") {
  return new WeatherWidget(containerId, location);
}
