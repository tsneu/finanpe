function loadChart(chart, endpoint) {
    $.ajax({
        url: endpoint,
        type: "GET",
        dataType: "json",
        success: (jsonResponse) => {
          // Extract data from the response
          const title = jsonResponse.title;
          const labels = jsonResponse.data.labels;
          const datasets = jsonResponse.data.datasets;

          // Reset the current chart
          chart.data.datasets = [];
          chart.data.labels = [];

          // Load new data into the chart
          chart.options.plugins.title.text = title;
          chart.options.plugins.title.display = true;
          chart.data.labels = labels;
          datasets.forEach(dataset => {
              chart.data.datasets.push(dataset);
          });
          chart.update();
        },
        error: () => console.log("Failed to fetch chart data from " + endpoint + "!")
      });
  }