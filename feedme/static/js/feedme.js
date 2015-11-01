var OrderLine = React.createClass({
    getInitialState: function() {
      return {
          orderline: {},
          hidden: false,
          showDelete: false,
          showEdit: false,
          showJoin: false,
          showLeave: false
      }
    },

    loadOrderLine: function(path) {
      $.ajax({
        url: path || api_base + "orderlines/" + this.props.olid,
        success: function(result) {
          // console.log(result)
          this.setState({orderline: result})
        }.bind(this),
        error: function(xhr, err, status) {
          console.log("Something went wrong.", xhr, err, status)
        }.bind(this)
      })
      this.setState({hideOrderLine: false})
    },

    componentDidMount: function() {
      this.loadOrderLine()
    },

    handleRemove: function(orderline) {
      this.setState({hideOrderLine: true})
      this.props.onRemoveOrderLine(orderline)
    },

    handleEdit: function(orderline) {
      // @ToDo: Make this better, and send a callback which updates this state
      // Place values in form
      $("#id").val(orderline.id)
      $("#menu_item").val(orderline.menu_item)
      $("#soda").val(orderline.soda)
      $("#extras").val(orderline.extras)
      $("#price").val(orderline.price)
      this.setState({hideOrderLine: true})
    },
    // @ToDo: join and leave events

    render: function() {
        var deleteButton = this.state.orderline.creator === username ? <DangerButton value="Delete" clickHandler={this.handleRemove.bind(this, this.state.orderline)} /> : ""
        var editButton = this.state.orderline.creator === username ? <PrimaryButton value="Edit" clickHandler={this.handleEdit.bind(this, this.state.orderline)} /> : ""
        var joinButton = this.state.orderline.creator !== username ? <PrimaryButton value="Join" clickHandler={this.handleJoin} /> : ""
        var leaveButton = this.state.orderline.creator !== username ? <PrimaryButton value="Leave" clickHandler={this.handleLeave} /> : ""
        return (
            <tr className={this.state.hideOrderLine ? 'hide' : ''} id={"orderline-" + this.state.orderline.id}>
                <td><b>{this.state.orderline.creator}</b> {this.state.orderline.users}</td>
                <td>{this.state.orderline.menu_item}</td>
                <td>{this.state.orderline.soda}</td>
                <td>{this.state.orderline.extras}</td>
                <td>{this.state.orderline.price}</td>
                <td><div className="btn-group">{joinButton} {leaveButton} {editButton} {deleteButton}</div></td>
            </tr>
        );
    }
});

var OrderLineForm = React.createClass({
    handleSubmit: function(e) {
      e.preventDefault();
      this.props.onOrderLineSubmit({
          id: this.refs.id.value,
          menu_item: this.refs.menu_item.value,
          soda: this.refs.soda.value,
          extras: this.refs.extras.value,
          price: this.refs.price.value
      });
      // Handle all the stuff
      this.refs.id.value = "";
      this.refs.menu_item.value = "";
      this.refs.soda.value = "";
      this.refs.extras.value = "";
      this.refs.price.value = "";
      return;
    },
    // @ToDo: Add buddy system (probably by sending pre-flight HTTP OPTIONS which should populate a list)

    render: function() {
        return (
            <form className="form orderLineForm" onSubmit={this.handleSubmit}>
                <input type="number" id="id" ref="id" hidden />
                <input type="text" placeholder="Menu item" id="menu_item" ref="menu_item" />
                <input type="text" placeholder="Soda" id="soda" ref="soda" />
                <input type="text" placeholder="Extras" id="extras" ref="extras" />
                <input type="number" placeholder="Price" id="price" ref="price" />
                <input type="submit" value="Save" className="btn btn-success btn-sm" />
            </form>
        );
    }
});

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
      <table className="table orderLineList">
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

/* Buttons */

var DangerButton = React.createClass({
    render: function() {
        return (
            <button className="btn btn-danger btn-sm" onClick={this.props.clickHandler}>{this.props.value}</button>
        )
    }
})

var PrimaryButton = React.createClass({
    render: function() {
        return (
            <button className="btn btn-primary btn-sm" onClick={this.props.clickHandler}>{this.props.value}</button>
        )
    }
})

var SuccessButton = React.createClass({
    render: function() {
        return (
            <button className="btn btn-success btn-sm" onClick={this.props.clickHandler}>{this.props.value}</button>
        )
    }
})

// @ToDo: Use "require" syntax for files
ReactDOM.render(
    <Order apiroot={"../feedme-api/"} url={"/feedme-api/orderlines/?order=" + order} />,
    document.getElementById("feedme-main")
);