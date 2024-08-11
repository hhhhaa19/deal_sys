$(function () {
    $.ajax({
        url: '/trade',
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            if (response.code === 200) {
                populateTable(response.data);
            } else {
                console.error('Failed to fetch orders:', response.msg);
            }
        },
        error: function (xhr, status, error) {
            console.error('Error fetching data:', error);
        }
    });
})

function populateTable(orders) {
    const $table = $('#ordersTable tbody');
    $table.empty(); // 清空表格当前内容
    orders.forEach(order => {
        const date = new Date(order.time).toLocaleString(); // 将时间戳转换为更易读的格式
        const trClass = order.isBuyer ? 'buyer' : 'seller';  // 根据isBuyer状态设置类名
        const row = `
                <tr class="${trClass}">
                    <td>${date}</td>
                    <td>${order.symbol}</td>
                    <td>${order.isBuyer ? '买入' : '卖出'}</td>
                    <td>${parseFloat(order.price).toFixed(2)}</td>
                    <td>${parseFloat(order.qty).toFixed(6)}</td>
                    <td>${parseFloat(order.quoteQty).toFixed(2)}</td>
                    <td>${parseFloat(order.commission).toFixed(6)}</td>
                    <td>${order.commissionAsset}</td>
                </tr>
            `;
        $table.append(row);
    });
}