$(document).ready(function() {
    // 获取钱包余额数据
    $.ajax({
        url: '/account', // 替换为你的后端API端点
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            const walletBalances = $('#wallet-balances');
            walletBalances.empty(); // 清空之前的内容

            data.forEach(function(item) {
                const balanceItem = $(`
                    <div class="balance-item">
                        <h2>${item.asset}</h2>
                        <p>Free: ${parseFloat(item.free).toFixed(8)}</p>
                        <p>Locked: ${parseFloat(item.locked).toFixed(8)}</p>
                    </div>
                `);
                walletBalances.append(balanceItem);
            });
        },
        error: function(error) {
            console.error('Error fetching Data:', error);
        }
    });

    // 获取图表数据
    $.ajax({
        url: '/award', // 替换为你的后端API端点
        method: 'GET',
        dataType: 'json',
        success: function(chartData) {
            const chart = echarts.init(document.getElementById('chart'));
            const timestamps = chartData.map(item => new Date(item[1]).toLocaleString()); // 获取时间戳并格式化
            const values = chartData.map(item => parseFloat(item[3])); // 获取资产值

            // 计算累计收益率
            const initialInvestment = values[0];
            const finalValue = values[values.length - 1];
            const cumulativeReturn = ((finalValue - initialInvestment) / initialInvestment) * 100;

            $('#cumulative-return').text(`Cumulative Return: ${cumulativeReturn.toFixed(2)}%`);

            const option = {
                title: {
                    text: 'Wallet Balance Over Time'
                },
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: timestamps
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    data: values,
                    type: 'line',
                    smooth: true,
                    areaStyle: {}
                }]
            };

            chart.setOption(option);
        },
        error: function(error) {
            console.error('Error fetching chart Data:', error);
        }
    });
});
