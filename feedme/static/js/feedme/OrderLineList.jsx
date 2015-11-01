var OrderLineList = React.createClass({
  handleRemoveOrderLine: function(orderline) {
    $.ajax({
        url: api_base + "orderlines/" + orderline.id,
        beforeSend: function(xhr) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        type: "DELETE",
        success: function(result) {
        }.bind(this),
          error: function(xhr, error, something) {
            console.log(xhr, error, something)
        }.bind(this)
    })
  },

  render: function() {
    var that = this
    var orderlines = this.props.data.map(function (orderline) {
        return (
            <OrderLine olid={orderline.id} key={orderline.id} onEditOrderLine={that.handleUpdateOrderLine} onRemoveOrderLine={that.handleRemoveOrderLine} />
        );
    });
    return (
      <table className="table table-striped orderLineList">
          <thead>
              <tr>
                  <th>User(s)</th>
                  <th>Menu item</th>
                  <th>Soda</th>
                  <th>Extras</th>
                  <th>Price</th>
                  <th>Status</th>
              </tr>
          </thead>
          <tbody>
            {orderlines}
          </tbody>
      </table>
    );
  }
});

window.OrderLineList = OrderLineList
module.exports = OrderLineList