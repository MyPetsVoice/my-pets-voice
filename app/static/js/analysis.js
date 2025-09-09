let charts = {};
let currentPetId = null;

document.addEventListener("DOMContentLoaded", function () {
  loadPetList();
});

// 펫 목록 불러오기
async function loadPetList() {
  try {
    const response = await fetch("/api/dailycares/get-pet/");
    const pets = await response.json();

    const petSelect = document.getElementById("petSelect");
    petSelect.innerHTML = '<option value="">반려동물을 선택하세요</option>';

    pets.forEach((pet) => {
      const option = document.createElement("option");
      option.value = pet.pet_id;
      option.textContent = `${pet.pet_name} (${pet.species_name})`;
      petSelect.appendChild(option);
    });

    // 첫 번째 펫이 있으면 자동 선택
    if (pets.length > 0) {
      petSelect.value = pets[0].pet_id;
      currentPetId = pets[0].pet_id;
      loadChartData();
    }
  } catch (error) {
    showError("펫 목록을 불러오는데 실패했습니다: " + error.message);
  }
}

// 모든 차트 섹션 숨기기
function hideAllChartSections() {
  // 요약 카드 숨기기 (첫 번째 chart-card)
  const summaryCard = document.querySelector(".chart-card");
  if (summaryCard) {
    summaryCard.style.display = "none";
  }

  // 트렌드 분석 카드 숨기기 (마지막 chart-card)
  const allCards = document.querySelectorAll(".chart-card");
  const lastCard = allCards[allCards.length - 1];
  if (lastCard) {
    lastCard.style.display = "none";
  }

  document.getElementById("chartSection1").style.display = "none";
  document.getElementById("chartSection2").style.display = "none";
  document.getElementById("chartSection3").style.display = "none";
  document.getElementById("chartSection4").style.display = "none";
  document.getElementById("medicationCard").style.display = "none";
  document.getElementById("noMedicationCard").style.display = "none";

  // 기존 차트들 제거
  Object.values(charts).forEach((chart) => chart.destroy());
  charts = {};

  // 트렌드 분석 초기화
  document.getElementById("trendAnalysis").innerHTML = "";
}

// 요약 블록 초기화
function resetSummaryBlocks() {
  document.getElementById("weightSummary").textContent = "분석 중...";
  document.getElementById("weightAvg").textContent = "평균 계산 중...";
  document.getElementById("foodSummary").textContent = "분석 중...";
  document.getElementById("foodAvg").textContent = "평균 계산 중...";
  document.getElementById("waterSummary").textContent = "분석 중...";
  document.getElementById("waterAvg").textContent = "평균 계산 중...";
  document.getElementById("exerciseSummary").textContent = "분석 중...";
  document.getElementById("exerciseAvg").textContent = "평균 계산 중...";
}

// 차트 데이터 불러오기
async function loadChartData() {
  const petId = document.getElementById("petSelect").value;
  const days = document.getElementById("periodSelect").value;

  if (!petId) {
    showError("반려동물을 선택해주세요.");
    hideAllChartSections();
    resetSummaryBlocks();
    return;
  }

  currentPetId = petId;
  showLoading(true);
  hideError();

  try {
    // 데이터 요청
    const [chartResponse, summaryResponse] = await Promise.all([
      fetch(`/api/dailycares/health-chart/${petId}?days=${days}`),
      fetch(`/api/dailycares/health-summary/${petId}?days=${days}`),
    ]);

    if (!chartResponse.ok || !summaryResponse.ok) {
      throw new Error("데이터 요청 실패");
    }

    const chartData = await chartResponse.json();

    if (chartData.dates.length === 0) {
      showError("선택한 기간에 건강 기록이 없습니다.");
      hideAllChartSections();
      resetSummaryBlocks();
      showLoading(false);
      return;
    }

    createCharts(chartData);
    generateWeekSummary(chartData);
    generateTrendAnalysis(chartData);
    checkMedicationStatus(petId);

    showLoading(false);

    // 요약 카드 다시 표시
    const summaryCard = document.querySelector(".chart-card");
    if (summaryCard) {
      summaryCard.style.display = "block";
    }

    // 트렌드 분석 카드 다시 표시
    const allCards = document.querySelectorAll(".chart-card");
    const lastCard = allCards[allCards.length - 1];
    if (lastCard) {
      lastCard.style.display = "block";
    }

    // 개별 차트 섹션들 표시
    document.getElementById("chartSection1").style.display = "block";
    document.getElementById("chartSection2").style.display = "block";
    document.getElementById("chartSection3").style.display = "block";
    document.getElementById("chartSection4").style.display = "block";
  } catch (error) {
    showError("데이터를 불러오는데 실패했습니다: " + error.message);
    hideAllChartSections();
    resetSummaryBlocks();
    showLoading(false);
  }
}

// 차트 생성
function createCharts(data) {
  Object.values(charts).forEach((chart) => chart.destroy());
  charts = {};

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#666" },
      },
      y: {
        beginAtZero: false,
        grid: { color: "rgba(0,0,0,0.1)" },
        ticks: { color: "#666" },
      },
    },
    plugins: {
      legend: { display: false },
    },
  };

  // 몸무게 차트
  const weightMin = Math.min(...data.weight);
  const weightMax = Math.max(...data.weight);
  const weightRange = weightMax - weightMin;
  const weightPadding = Math.max(0.5, weightRange * 0.1);

  charts.weight = new Chart(document.getElementById("weightChart"), {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        {
          data: data.weight,
          borderColor: "#ff6b6b",
          backgroundColor: "rgba(255, 107, 107, 0.1)",
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: "#ff6b6b",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
          pointRadius: 5,
        },
      ],
    },
    options: {
      ...commonOptions,
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          min: Math.max(0, weightMin - weightPadding),
          max: weightMax + weightPadding,
          title: { display: true, text: "몸무게 (kg)", color: "#666" },
        },
      },
    },
  });

  // 식사량 차트
  charts.food = new Chart(document.getElementById("foodChart"), {
    type: "bar",
    data: {
      labels: data.dates,
      datasets: [
        {
          data: data.food,
          backgroundColor: "rgba(78, 205, 196, 0.8)",
          borderColor: "#4ecdc4",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      ...commonOptions,
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          beginAtZero: true, // 식사량은 0부터 시작
          title: { display: true, text: "식사량 (g)", color: "#666" },
        },
      },
    },
  });

  // 수분 섭취량 차트
  charts.water = new Chart(document.getElementById("waterChart"), {
    type: "bar",
    data: {
      labels: data.dates,
      datasets: [
        {
          data: data.water,
          backgroundColor: "rgba(69, 170, 242, 0.8)",
          borderColor: "#45aaf2",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      ...commonOptions,
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          beginAtZero: true,
          title: { display: true, text: "수분량 (ml)", color: "#666" },
        },
      },
    },
  });

  // 활동량 차트
  charts.exercise = new Chart(document.getElementById("exerciseChart"), {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        {
          data: data.exercise,
          borderColor: "#a55eea",
          backgroundColor: "rgba(165, 94, 234, 0.1)",
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: "#a55eea",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
          pointRadius: 5,
        },
      ],
    },
    options: {
      ...commonOptions,
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          beginAtZero: true,
          title: { display: true, text: "활동시간 (분)", color: "#666" },
        },
      },
    },
  });
}

// 최근 7일 한줄 요약 생성
function generateWeekSummary(chartData) {
  const data = chartData;

  // 최근 7일 데이터만 추출
  const recentData = {
    weight: data.weight.slice(-7),
    food: data.food.slice(-7),
    water: data.water.slice(-7),
    exercise: data.exercise.slice(-7),
  };

  // 각 항목별 분석 및 평균
  const weightAnalysis = analyzeWeightTrend(recentData.weight);
  const foodAnalysis = analyzeFoodTrend(recentData.food);
  const waterAnalysis = analyzeWaterTrend(recentData.water);
  const exerciseAnalysis = analyzeExerciseTrend(recentData.exercise);

  // 트렌드 텍스트 설정
  document.getElementById("weightSummary").textContent = weightAnalysis.trend;
  document.getElementById("weightAvg").textContent = weightAnalysis.average;

  document.getElementById("foodSummary").textContent = foodAnalysis.trend;
  document.getElementById("foodAvg").textContent = foodAnalysis.average;

  document.getElementById("waterSummary").textContent = waterAnalysis.trend;
  document.getElementById("waterAvg").textContent = waterAnalysis.average;

  document.getElementById("exerciseSummary").textContent =
    exerciseAnalysis.trend;
  document.getElementById("exerciseAvg").textContent = exerciseAnalysis.average;
}

// 몸무게 트렌드 분석
function analyzeWeightTrend(weights) {
  if (weights.length < 2) return { trend: "데이터 부족", average: "" };

  const first = weights[0];
  const last = weights[weights.length - 1];
  const change = last - first;
  const avg = (weights.reduce((a, b) => a + b, 0) / weights.length).toFixed(1);

  let trendText = "";
  if (Math.abs(change) < 0.1) {
    trendText = "안정적 유지";
  } else if (change > 0) {
    trendText = `${change.toFixed(1)}kg 증가`;
  } else {
    trendText = `${Math.abs(change).toFixed(1)}kg 감소`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}kg`,
  };
}

// 식사량 트렌드 분석
function analyzeFoodTrend(foods) {
  if (foods.length < 2) return { trend: "데이터 부족", average: "" };

  const avg = (foods.reduce((a, b) => a + b, 0) / foods.length).toFixed(0);

  // 전체 트렌드 계산 (첫 값과 마지막 값 비교)
  const first = foods[0];
  const last = foods[foods.length - 1];
  const overallChange = ((last - first) / first) * 100;

  // 연속적인 변화 감지
  let isDecreasing = true;
  let isIncreasing = true;

  for (let i = 1; i < foods.length; i++) {
    if (foods[i] > foods[i - 1]) isDecreasing = false;
    if (foods[i] < foods[i - 1]) isIncreasing = false;
  }

  let trendText = "";
  if (isDecreasing && Math.abs(overallChange) > 15) {
    trendText = `지속적 감소 (${Math.abs(overallChange).toFixed(0)}%↓)`;
  } else if (isIncreasing && Math.abs(overallChange) > 15) {
    trendText = `지속적 증가 (${overallChange.toFixed(0)}%↑)`;
  } else if (Math.abs(overallChange) > 25) {
    trendText =
      overallChange > 0
        ? `섭취량 증가 (+${overallChange.toFixed(0)}%↑)`
        : `섭취량 감소 (${Math.abs(overallChange).toFixed(0)}%↓)`;
  } else {
    trendText = "일정한 섭취";
  }

  return {
    trend: trendText,
    average: `평균 ${avg}g`,
  };
}

// 수분 섭취 트렌드 분석
function analyzeWaterTrend(waters) {
  if (waters.length < 2) return { trend: "데이터 부족", average: "" };

  const avg = (waters.reduce((a, b) => a + b, 0) / waters.length).toFixed(0);
  const first = waters[0];
  const last = waters[waters.length - 1];
  const overallChange = ((last - first) / first) * 100;

  let trendText = "";
  if (Math.abs(overallChange) < 20) {
    trendText = "일정한 수준";
  } else if (overallChange > 0) {
    trendText = `섭취량 증가 (+${overallChange.toFixed(0)}%↑)`;
  } else {
    trendText = `섭취량 감소 (${Math.abs(overallChange).toFixed(0)}%↓)`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}ml`,
  };
}

// 활동량 트렌드 분석
function analyzeExerciseTrend(exercises) {
  if (exercises.length < 2) return { trend: "데이터 부족", average: "" };

  const avg = (exercises.reduce((a, b) => a + b, 0) / exercises.length).toFixed(
    0
  );
  const first = exercises[0];
  const last = exercises[exercises.length - 1];
  const change = last - first;

  let trendText = "";
  if (Math.abs(change) < 10) {
    trendText = "일정한 활동량";
  } else if (change > 0) {
    trendText = `활동량 증가 (+${change.toFixed(0)}분)`;
  } else {
    trendText = `활동량 감소 (${Math.abs(change).toFixed(0)}분)`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}분`,
  };
}

// 7일 트렌드 분석 생성
function generateTrendAnalysis(chartData) {
  const container = document.getElementById("trendAnalysis");
  const insights = generateInsights(chartData);

  container.innerHTML = insights
    .map(
      (insight) => `
        <div class="trend-card" style="background: ${insight.bgColor}; border-left: 4px solid ${insight.borderColor};">
            <strong style="color: ${insight.textColor};">${insight.icon} ${insight.title}</strong>
            <p style="margin: 10px 0 0 0; color: #666;">${insight.description}</p>
        </div>
    `
    )
    .join("");
}

function generateInsights(data) {
  const insights = [];
  const recentData = {
    weight: data.weight.slice(-7),
    food: data.food.slice(-7),
    water: data.water.slice(-7),
    exercise: data.exercise.slice(-7),
  };

  // 꾸준한 기록 체크
  const recordDays = data.dates.length;
  if (recordDays >= 7) {
    insights.push({
      icon: "📝",
      title: "꾸준한 기록",
      description: `최근 ${recordDays}일간 건강 기록을 성실히 작성하고 계시네요. 지속적인 관리가 핵심입니다. 좀 더 파이팅`,
      bgColor: "#e8f5e8",
      borderColor: "#4caf50",
      textColor: "#2e7d32",
    });
  }

  // 몸무게 분석
  const weightVariance = calculateVariance(recentData.weight);
  if (weightVariance < 0.3) {
    insights.push({
      icon: "⚖️",
      title: "안정적인 체중",
      description:
        "체중이 안정적으로 유지되고 있어요. 현재 관리 방식을 계속 유지하시면 좋겠습니다.",
      bgColor: "#e8f5e8",
      borderColor: "#4caf50",
      textColor: "#2e7d32",
    });
  } else if (weightVariance > 0.5) {
    insights.push({
      icon: "📊",
      title: "체중 변화 관찰",
      description:
        "체중에 변화가 있어요. 식사량이나 활동량과의 연관성을 살펴보시기 바랍니다.",
      bgColor: "#fff3e0",
      borderColor: "#ff9800",
      textColor: "#f57c00",
    });
  }

  // 식사량 분석
  recentData.food.reduce((a, b) => a + b, 0) / recentData.food.length;
  const foodFirst = recentData.food[0];
  const foodLast = recentData.food[recentData.food.length - 1];
  const foodChange = ((foodLast - foodFirst) / foodFirst) * 100;

  if (Math.abs(foodChange) > 30) {
    if (foodChange < 0) {
      insights.push({
        icon: "🍽️",
        title: "식사량 감소 주의",
        description: `최근 식사량이 ${Math.abs(foodChange).toFixed(
          0
        )}% 감소했어요. 건강상태를 확인해보시기 바랍니다.`,
        bgColor: "#fff3e0",
        borderColor: "#ff9800",
        textColor: "#f57c00",
      });
    } else {
      insights.push({
        icon: "🍽️",
        title: "식사량 증가",
        description: `최근 식사량이 ${foodChange.toFixed(
          0
        )}% 증가했어요. 적정량 유지에 주의하세요.`,
        bgColor: "#e3f2fd",
        borderColor: "#2196f3",
        textColor: "#1976d2",
      });
    }
  }

  // 수분 섭취 분석
  const avgWater =
    recentData.water.reduce((a, b) => a + b, 0) / recentData.water.length;
  if (avgWater < 180) {
    insights.push({
      icon: "💧",
      title: "수분 섭취 부족",
      description: `하루 평균 ${avgWater.toFixed(
        0
      )}ml로 수분 섭취가 부족할 수 있어요. 충분한 수분 공급을 권장합니다.`,
      bgColor: "#e3f2fd",
      borderColor: "#2196f3",
      textColor: "#1976d2",
    });
  } else if (avgWater > 400) {
    insights.push({
      icon: "💧",
      title: "충분한 수분 섭취",
      description: `하루 평균 ${avgWater.toFixed(
        0
      )}ml로 충분한 수분을 섭취하고 있어요.`,
      bgColor: "#e8f5e8",
      borderColor: "#4caf50",
      textColor: "#2e7d32",
    });
  }

  // 활동량 분석
  const avgExercise =
    recentData.exercise.reduce((a, b) => a + b, 0) / recentData.exercise.length;
  if (avgExercise > 60) {
    insights.push({
      icon: "🏃‍♂️",
      title: "활발한 활동",
      description: `평균 ${avgExercise.toFixed(
        0
      )}분의 활동으로 충분한 운동량을 유지하고 있어요.`,
      bgColor: "#e8f5e8",
      borderColor: "#4caf50",
      textColor: "#2e7d32",
    });
  } else if (avgExercise < 30) {
    insights.push({
      icon: "🚶‍♂️",
      title: "활동량 늘리기",
      description:
        "활동량이 다소 적은 편이에요. 날씨가 좋은 날 산책 시간을 조금 늘려보는 건 어떨까요?",
      bgColor: "#e3f2fd",
      borderColor: "#2196f3",
      textColor: "#1976d2",
    });
  }

  // 기본 격려 메시지
  if (insights.length < 2) {
    insights.push({
      icon: "💡",
      title: "건강 관리 팁",
      description:
        "꾸준한 기록과 관찰이 반려동물 건강 관리의 첫걸음입니다. 변화가 있을 때는 수의사와 상담해보세요.",
      bgColor: "#e3f2fd",
      borderColor: "#2196f3",
      textColor: "#1976d2",
    });
  }

  return insights;
}

// 약물 상태 확인
async function checkMedicationStatus(petId) {
  try {
    const response = await fetch(`/api/dailycares/medications/${petId}`);
    const medications = await response.json();

    if (medications.length > 0) {
      document.getElementById("medicationCard").style.display = "block";

      const currentMeds = medications.filter(
        (med) => !med.end_date || new Date(med.end_date) > new Date()
      );

      document.getElementById("medicationStatus").innerHTML = `
                <p>현재 ${currentMeds.length}개 약물 복용 중</p>
                <small style="color: #666;">꾸준한 복용 관리가 중요해요</small>
            `;
    } else {
      document.getElementById("noMedicationCard").style.display = "block";
    }
  } catch (error) {
    document.getElementById("noMedicationCard").style.display = "block";
  }
}

function calculateVariance(data) {
  const mean = data.reduce((a, b) => a + b, 0) / data.length;
  const variance =
    data.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / data.length;
  return Math.sqrt(variance);
}

// 로딩 표시
function showLoading(show) {
  document.getElementById("loadingDiv").style.display = show ? "block" : "none";
}

// 에러 표시
function showError(message) {
  const errorDiv = document.getElementById("errorDiv");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
  showLoading(false);
}

// 에러 숨기기
function hideError() {
  document.getElementById("errorDiv").style.display = "none";
}

// 펫 선택 변경 시
document.getElementById("petSelect").addEventListener("change", function () {
  if (this.value) {
    currentPetId = this.value;
    loadChartData();
  }
});

// 기간 선택 변경 시
document.getElementById("periodSelect").addEventListener("change", function () {
  if (currentPetId) {
    loadChartData();
  }
});
