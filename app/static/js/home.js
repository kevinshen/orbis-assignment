$(document).ready(function() {
  $('#parse').click(function() {

      var etf = $('#etf').val().toUpperCase();
      console.log('hi')
 
        $.ajax({
            url: '/parse',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function(response) {
                console.log(response);
                console.log(response['top_holdings']);
                console.log(response['country_weights']);
                console.log(response['sector_weights']);

                $('h1').text('Fund Data (' + etf + ')');

                holdingsTable(response['top_holdings']);
                holdingsChart(response['top_holdings']);
                countryChart(response['country_weights']);
                sectorChart(response['sector_weights']);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});

function holdingsTable(data) {
    $('#html-table').empty();
    if (data == null) return;
    var len = Object.keys(data['holding']).length;
    if (len == 0) return;
    var tableHTML = '<table class="table table-striped table-hover"><thead><tr>'
                    + '<th>Name</th>'
                    + '<th>Weight</th>'
                    + '<th>Shares</th></tr></thead>';
    tableHTML += '<tbody>';
    for (var i = 0; i < len; i++) {
        tableHTML += '<tr>';
        tableHTML += '<th scope="row">' + data['holding'][i] + '</th>';
        tableHTML += '<td>' + data['weight'][i] + '&#37;</th>';
        tableHTML += '<td>' + data['shares'][i] + '</th>';
        tableHTML += '</tr>';
    }
    tableHTML += '</tbody></table>';

    $('#html-table').append(tableHTML);
}

function holdingsChart(data) {
    $('#holdings-bar').empty();
    if (data == null) return;
    var len = Object.keys(data['holding']).length;
    if (len == 0) return;
    var holdings = [];
    var values = [];
    for (var i = 0; i < len; i++) {
        holdings.push(data['holding'][i]);
        values.push({y:data['weight'][i], z:data['shares'][i]});
    }
    $(function () {
        $('#holdings-bar').highcharts({
            credits: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            chart: {
                type: 'column'
            },
            title: {
                text: 'Top 10 Holdings'
            },
            xAxis: {
                categories: holdings,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Weight'
                },
                labels: {
                    formatter:function() {
                        return Highcharts.numberFormat(this.value,0,',') + '%';
                    }
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">Weight: </td>' +
                    '<td style="padding:0"><b>{point.y:.2f}%</b></td></tr>'+
                    '<tr><td style="color:{series.color};padding:0">Shares: </td>' +
                    '<td style="padding:0"><b>{point.z} shares</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                name: 'Holding',
                data: values
            }]
        });
    });
}

function countryChart(data) {
    $('#country-pie').empty();
    if (data == null) return;
    var len = Object.keys(data['country']).length;
    if (len == 0) return;
    var values = [];
    for (var i = 0; i < len; i++) {
        values.push({name:data['country'][i], y:data['weight'][i]});
    }
    $(function () {
        $('#country-pie').highcharts({
            credits: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: 'Country Weight'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    showInLegend: true
                }
            },
            series: [{
                name: 'Weight',
                colorByPoint: true,
                data: values
            }]
        });
    });
}

function sectorChart(data) {
    $('#sector-pie').empty();
    if (data == null) return;
    var len = Object.keys(data['sector']).length;
    if (len == 0) return;
    var values = [];
    for (var i = 0; i < len; i++) {
        values.push({name:data['sector'][i], y:data['weight'][i]});
    }
    $(function () {
        $('#sector-pie').highcharts({
            credits: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: 'Sector Weight'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    showInLegend: true
                }
            },
            series: [{
                name: 'Weight',
                colorByPoint: true,
                data: values
            }]
        });
    });
}


$(function() {
    $("form input").keypress(function (e) {
        if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
            $('#parse').click();
            return false;
        } else {
            return true;
        }
    });
});