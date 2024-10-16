$(document).ready(function () {
    // 更新交易对按钮点击事件
    $('#change-pair').click(function () {
        var newPair = $('#trading-pair-select').val(); // 获取选择框中的值
        $.ajax({
            url: '/update_trading_pair',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({trading_pair: newPair}),
            success: function () {
                $('#trading-pair').text(newPair);
                alert('交易对已更新为: ' + newPair);
            },
            error: function (response) {
                var errorMessage = response.responseJSON ? response.responseJSON.error : response.responseText;
                alert('更新失败: ' + errorMessage);
            }
        });
    });

    // 开始交易按钮点击事件
    $('#start-trading').click(function () {
        $.ajax({
            url: '/start_trading',
            type: 'GET',
            success: function (response) {
                alert(response.status);
            },
            error: function (response) {
                alert('无法开始交易: ' + response.responseJSON.status);
            }
        });
    });

    // 结束交易按钮点击事件
    $('#stop-trading').click(function () {
        $.ajax({
            url: '/stop_trading',
            type: 'GET',
            success: function (response) {
                alert(response.status);
            },
            error: function (response) {
                alert('无法结束交易: ' + response.responseJSON.status);
            }
        });
    });

    // 其他按钮事件处理...
    // 定时获取日志的函数
    function fetchLogs() {
        $.ajax({
            url: '/get_logs',
            type: 'GET',
            success: function (response) {
                var logs = response.logs;
                var logContainer = $('#log-entries');
                logContainer.empty(); // 清空当前日志
                logs.forEach(function (log) {
                    logContainer.append('<p>' + log + '</p>');
                });
                // 保持滚动条在最底部
                var logDiv = document.getElementById('log-container');
                logDiv.scrollTop = logDiv.scrollHeight;
            },
            error: function () {
                console.log('无法获取日志');
            }
        });
    }

    // 每5秒钟获取一次日志
    setInterval(fetchLogs, 5000);
});
