(function () {
    function getText(labelMap, key, fallback) {
        return labelMap[key] || fallback;
    }

    function setActiveButtons(buttons, activeValue, dataKey) {
        buttons.forEach((button) => {
            const isActive = button.dataset[dataKey] === activeValue;
            button.classList.toggle("active", isActive);
            if (isActive && button.classList.contains("btn-outline-primary")) {
                button.classList.replace("btn-outline-primary", "btn-primary");
            } else if (!isActive && button.classList.contains("btn-primary")) {
                button.classList.replace("btn-primary", "btn-outline-primary");
            }

            if (isActive && button.classList.contains("btn-outline-secondary")) {
                button.classList.replace("btn-outline-secondary", "btn-secondary");
            } else if (!isActive && button.classList.contains("btn-secondary")) {
                button.classList.replace("btn-secondary", "btn-outline-secondary");
            }
        });
    }

    function buildSubtitle(metric, period, count) {
        const metricText = metric === "views" ? "views" : "downloads";
        const periodText = period === "month" ? "this month" : "this week";
        if (count === 0) {
            return `No ${metricText} recorded for ${periodText}.`;
        }
        return `Showing top ${count} datasets by ${metricText} (${periodText}).`;
    }

    document.addEventListener("DOMContentLoaded", () => {
        const trendingList = document.getElementById("trending-list");
        const trendingStatus = document.getElementById("trending-status");
        const emptyState = document.getElementById("trending-empty-state");

        if (!trendingList || !trendingStatus || !emptyState) {
            return;
        }

        const metricButtons = document.querySelectorAll("[data-trending-metric]");
        const periodButtons = document.querySelectorAll("[data-trending-period]");

        let metric = "downloads";
        let period = "week";

        metricButtons.forEach((button) => {
            button.addEventListener("click", () => {
                metric = button.dataset.trendingMetric;
                setActiveButtons(metricButtons, metric, "trendingMetric");
                loadTrending();
            });
        });

        periodButtons.forEach((button) => {
            button.addEventListener("click", () => {
                period = button.dataset.trendingPeriod;
                setActiveButtons(periodButtons, period, "trendingPeriod");
                loadTrending();
            });
        });

        setActiveButtons(metricButtons, metric, "trendingMetric");
        setActiveButtons(periodButtons, period, "trendingPeriod");
        loadTrending();

        function loadTrending() {
            trendingStatus.textContent = `Loading ${getText({ downloads: "downloads", views: "views" }, metric, "downloads")}...`;
            fetch(`/datasets/trending?metric=${metric}&period=${period}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Request failed");
                    }
                    return response.json();
                })
                .then((data) => {
                    renderTrending(data.results || []);
                })
                .catch(() => {
                    trendingList.innerHTML = "";
                    emptyState.classList.remove("d-none");
                    emptyState.textContent = "Something went wrong while loading trending datasets.";
                    trendingStatus.textContent = "Unable to load trending datasets right now.";
                });
        }

        function renderTrending(results) {
            trendingList.innerHTML = "";

            if (!results.length) {
                emptyState.classList.remove("d-none");
                trendingStatus.textContent = buildSubtitle(metric, period, 0);
                return;
            }

            emptyState.classList.add("d-none");
            trendingStatus.textContent = buildSubtitle(metric, period, results.length);

            results.forEach((item, index) => {
                const card = document.createElement("div");
                card.className = "col-12";
                const metricLabel = metric === "views" ? "views" : "downloads";
                const communityRow = item.community
                    ? `<span class="badge bg-light text-dark">${item.community}</span>`
                    : "";
                card.innerHTML = `
                    <div class="card trending-card ${index === 0 ? "trending-card-featured" : ""}">
                        <div class="card-body d-flex align-items-start">
                            <div class="trending-rank me-3">${index + 1}</div>
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                                    <div>
                                        <h4 class="mb-1">
                                            <a href="${item.doi}" class="text-decoration-none">${item.title}</a>
                                        </h4>
                                        <div class="text-secondary small">
                                            ${item.main_author ? `by ${item.main_author}` : "Main author not provided"}
                                        </div>
                                        ${communityRow ? `<div class="text-secondary small">${communityRow}</div>` : ""}
                                    </div>
                                    <span class="badge bg-primary">${item.total} ${metricLabel}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                trendingList.appendChild(card);
            });
        }
    });
})();
