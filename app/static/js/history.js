$(document).ready(function() {
    $.ajax({
        url: '/get_history',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log(response);

            $('h1').text('History');
            historyTable(response);
        },
        error: function(error) {
            console.log(error);
        }        
    });
});

function historyTable(data) {
    $('#html-table').empty();
    var len = Object.keys(data['etf_list']).length;
    if (len == 0) return;
    var tableHTML = '<table class="table table-striped table-hover"><thead><tr>'
                    + '<th>ETF</th>'
                    + '<th>Timestamp</th></tr></thead>';
    tableHTML += '<tbody>';
    for (var i = 0; i < len; i++) {
        tableHTML += '<tr>';
        tableHTML += '<th scope="row">' + data['etf_list'][i] + '</th>';
        tableHTML += '<td>' + data['timestamp'][i] + '</th>';
        tableHTML += '</tr>';
    }
    tableHTML += '</tbody></table>';

    $('#html-table').append(tableHTML);
}