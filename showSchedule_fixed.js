        // 계획표 표시 (수정된 버전)
        async function showSchedule() {
            document.getElementById('schedule-content').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <div>계획표를 불러오는 중...</div>
                </div>
            `;
            
            new bootstrap.Modal(document.getElementById('scheduleModal')).show();
            
            try {
                const response = await fetch('/api/schedule/monthly');
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                let html = `
                    <div class="text-center mb-4">
                        <h5 class="text-primary">${data.month_name || '2025년 9월'} 전체 발행 계획</h5>
                        <p class="text-muted">🔥 실시간 트렌드가 반영된 스케줄</p>
                    </div>
                    <div class="row">
                `;
                
                // 두 가지 API 응답 형식 모두 지원 (로컬/운영)
                if (data.schedule) {
                    let scheduleData;
                    
                    // 운영 환경: {1: {site: {primary: ..., secondary: ...}}, 2: {...}}
                    if (!Array.isArray(data.schedule) && typeof data.schedule === 'object') {
                        scheduleData = Object.keys(data.schedule).map(day => {
                            const dayData = data.schedule[day];
                            return {
                                date: `2025-09-${day.padStart(2, '0')}`,
                                day_name: ['일', '월', '화', '수', '목', '금', '토'][new Date(2025, 8, parseInt(day)).getDay()],
                                sites: dayData
                            };
                        }).sort((a, b) => new Date(a.date) - new Date(b.date));
                    } 
                    // 로컬 환경: [{date: ..., sites: [...]}, ...]
                    else if (Array.isArray(data.schedule)) {
                        scheduleData = data.schedule;
                    }
                    
                    if (scheduleData) {
                        scheduleData.forEach(dayInfo => {
                            try {
                                const { date, day_name, sites } = dayInfo;
                                const dayNum = new Date(date).getDate();
                                const hasSchedule = sites && typeof sites === 'object' && Object.keys(sites).length > 0;
                                
                                let dayContent = '';
                                if (hasSchedule) {
                                    Object.entries(sites).forEach(([siteName, siteData]) => {
                                        if (siteData) {
                                            dayContent += `
                                                <div class="mb-2">
                                                    <strong class="site-badge site-${siteName}">${siteName.toUpperCase()}</strong>
                                            `;
                                            
                                            // 운영 환경: primary/secondary 구조
                                            if (siteData.primary && siteData.secondary) {
                                                dayContent += `<div class="small mt-1">1. ${siteData.primary.topic}</div>`;
                                                dayContent += `<div class="small mt-1">2. ${siteData.secondary.topic}</div>`;
                                            }
                                            // 로컬 환경: 배열 구조
                                            else if (Array.isArray(siteData) && siteData.length > 0) {
                                                dayContent += siteData.map((topic, i) => 
                                                    `<div class="small mt-1">${i+1}. ${topic.topic || topic}</div>`
                                                ).join('');
                                            }
                                            
                                            dayContent += '</div>';
                                        }
                                    });
                                }
                                
                                html += `
                                    <div class="col-md-4 col-lg-3 mb-3">
                                        <div class="card ${hasSchedule ? 'border-primary' : 'border-light'}">
                                            <div class="card-header bg-light d-flex justify-content-between">
                                                <strong>${dayNum}일 (${day_name})</strong>
                                                ${hasSchedule ? '<span class="badge bg-success">8개</span>' : '<span class="badge bg-light text-muted">휴일</span>'}
                                            </div>
                                            <div class="card-body p-2 small">
                                                ${dayContent || '<div class="text-muted">스케줄 없음</div>'}
                                            </div>
                                        </div>
                                    </div>
                                `;
                            } catch (dayError) {
                                console.error('Day processing error:', dayError, dayInfo);
                            }
                        });
                    }
                } else {
                    html += '<div class="col-12 text-center text-muted">스케줄 데이터가 없습니다.</div>';
                }
                
                html += '</div>';
                document.getElementById('schedule-content').innerHTML = html;
                
            } catch (error) {
                console.error('Schedule error:', error);
                document.getElementById('schedule-content').innerHTML = `
                    <div class="text-center text-danger">
                        <h6>계획표를 불러올 수 없습니다</h6>
                        <p class="small">오류: ${error.message}</p>
                        <button class="btn btn-sm btn-outline-primary" onclick="showSchedule()">다시 시도</button>
                    </div>
                `;
            }
        }