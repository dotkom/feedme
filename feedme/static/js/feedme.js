var OrderLine = React.createClass({
    getInitialState: function() {
      return {orderline: {}}
    },
    componentDidMount: function() {
      this.setState({orderline: this.props.orderline})
    },
    render: function() {
        return (
            <tr>
                <td><b>{this.state.orderline.creator}</b> {this.state.orderline.users}</td>
                <td>{this.state.orderline.menu_item}</td>
                <td>{this.state.orderline.soda}</td>
                <td>{this.state.orderline.extras}</td>
                <td>{this.state.orderline.price}</td>
            </tr>
        );
    }
});

var OrderLineForm = React.createClass({
    handleSubmit: function(e) {
      e.preventDefault();
      this.props.onOrderLineSubmit({
          menu_item: this.refs.menu_item.value,
          soda: this.refs.soda.value,
          extras: this.refs.extras.value,
          price: this.refs.price.value
      });
      // Handle all the stuff
      this.refs.menu_item.value = "";
      this.refs.soda.value = "";
      this.refs.extras.value = "";
      this.refs.price.value = "";
      return;
    },
    render: function() {
        return (
            <form className="form orderLineForm" onSubmit={this.handleSubmit}>
                <input type="text" placeholder="Menu item" ref="menu_item" />
                <input type="text" placeholder="Soda" ref="soda" />
                <input type="text" placeholder="Extras" ref="extras" />
                <input type="number" placeholder="Price" ref="price" />
                <input type="submit" value="Post" />
            </form>
        );
    }
});

var OrderLineList = React.createClass({
  render: function() {
    var orderlines = this.props.data.map(function (orderline) {
        return (
            <OrderLine key={orderline.id} orderline={orderline} />
        );
    });
    return (
      <table className="table orderLineList">
          <thead>
              <tr>
                  <th>User(s)</th>
                  <th>Menu item</th>
                  <th>Soda</th>
                  <th>Extras</th>
                  <th>Price</th>
              </tr>
          </thead>
          <tbody>
            {orderlines}
          </tbody>
      </table>
    );
  }
});

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
    orderline.csrfmiddlewaretoken = csrftoken; // plz no hackerino
    orderline.order = order;
    $.ajax({
        url: this.props.url,
        dateType: 'json',
        type: 'POST',
        data: orderline,
        success: function(response) {
            this.setState({data: this.state.data.concat(response)})
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
        <OrderLineList data={this.state.data} />
        <OrderLineForm onOrderLineSubmit={this.handleOrderLineSubmit} />
      </div>
    );
  }
});

ReactDOM.render(
    <Order url={"/feedme-api/orderlines/?order=" + order} />,
    document.getElementById("feedme-main")
);