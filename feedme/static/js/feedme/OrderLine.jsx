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
      $("#users").val(orderline.users)
      this.setState({hideOrderLine: true})

      // On form submit, reload current orderline
      var that = this
      $("#formSubmit").click(function() {
        setTimeout(function() {
          that.loadOrderLine()
        }, 500) // I hope 500ms is enough to wait for a POST request to complete.
      })
    },
    // @ToDo: join and leave events

    render: function() {
        var deleteButton =  this.state.orderline.creator === username ? <Button value="Delete" type="danger" clickHandler={this.handleRemove.bind(this, this.state.orderline)} /> : ""
        var editButton = this.state.orderline.creator === username ? <Button value="Edit" type="primary" clickHandler={this.handleEdit.bind(this, this.state.orderline)} /> : ""
        var joinButton = this.state.orderline.creator !== username ? <Button value="Join" type="primary" clickHandler={this.handleJoin} /> : ""
        var leaveButton = this.state.orderline.creator !== username ? <Button value="Leave" type="primary" clickHandler={this.handleLeave} /> : ""
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

window.OrderLine = OrderLine
module.exports = OrderLine