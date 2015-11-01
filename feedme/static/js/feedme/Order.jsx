var Order = React.createClass({
  loadOrderLines: function(path) {
      $.ajax({
      url: path || this.props.url,
      dataType: 'json',
      cache: false,
      success: function(success) {
        var data = this.state.data;
        for (var attrname in success.results) {data[success.results[attrname].id] = success.results[attrname]; }
        this.setState({data: data});
        if (success.next != null) {
            this.loadOrderLines(success.next)
        }
      }.bind(this),
      error: function(xhr, status, error) {
        console.error(xhr, status, error)
      }.bind(this)
    });
  },

  handleOrderLineSubmit: function(orderline) {
    // Submit to server and refresh list
    orderline.csrfmiddlewaretoken = csrftoken;
    orderline.order = order;
    console.log("posting stuff ", orderline, " to ", (api_base) + "orderlines/" + (shouldPut ? orderline.id : ''))
    var shouldPut = orderline.id !== ""
    $.ajax({
        url: api_base + "orderlines/" + (shouldPut ? orderline.id : ''),
        beforeSend: function(xhr) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        dateType: 'json',
        type: shouldPut ? 'PUT' : 'POST',
        data: orderline,
        success: function(response) {
            console.log(response)
            if (shouldPut) {
                var data = this.state.data
                for (var attrname in response) {data[response[attrname].id] = response[attrname]; }
                this.setState({data: data})
                $("#orderline-" + response.id).removeClass("hide") // hacky way to show it again afterwards
            } else {
                this.setState({data: this.state.data.concat(response)})
            }
        }.bind(this),
        error: function(xhr, status, error) {
            console.error(xhr, status, error)
        }.bind(this)
    });
  },

  getInitialState: function() {
    return {data: []}
  },

  componentDidMount: function() {
    this.loadOrderLines()
  },

  render: function() {
    return (
      <div className="order">
        <h1>Order lines</h1>
        <OrderLineList data={this.state.data} url={this.props.url} apiroot={this.props.apiroot} />
        <OrderLineForm onOrderLineSubmit={this.handleOrderLineSubmit} />
      </div>
    );
  }
});

window.Order = Order
module.exports = Order
