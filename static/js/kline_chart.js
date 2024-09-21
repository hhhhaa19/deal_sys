$(document).ready(function () {
    $.ajax({
        url: '/api/kline',
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log(data)
            if (!data || !data.categories || !data.values) {
                console.error('Data is incomplete or not in the expected format');
                return;
            }
            var chartDom = document.getElementById('chart');
            var myChart = echarts.init(chartDom, null, {renderer: 'canvas', width: 'auto', height: 'auto'});
            var option = {
                xAxis: {
                    type: 'category',
                    data: data.categories
                },
                yAxis: {
                    type: 'value',
                    scale: true  // 添加这个属性可以让ECharts根据数据自动调整Y轴范围
                },
                series: [{
                    type: 'candlestick',
                    data: data.values
                }]
            };
            myChart.setOption(option);
        },
        error: function (xhr, status, error) {
            console.error('Error fetching Data:', error);
        }
    });
});