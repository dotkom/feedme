var OrderLine = React.createClass({
    getInitialState: function() {
      return {
          orderline: {},
          users: [],
          hidden: false,
          showDelete: false,
          showEdit: false,
          showJoin: false,
          showLeave: false
      }
    },

    componentDidMount: function() {
      this.loadOrderLine()
    },

    loadOrderLine: function(path) {
      $.ajax({
        url: path || api_base + "orderlines/" + this.props.olid + "/",
        success: function(result) {
          this.setState({orderline: result, users: result.users})
        }.bind(this),
        error: function(xhr, err, status) {
          console.log("Something went wrong.", xhr, err, status)
        }.bind(this)
      })
      this.setState({hideOrderLine: false})
    },

    generateAlert: function(type, message) {
      var alert_message = "<div class=\"alert alert-" + type + "\"><a class=\"close\" data-dismiss=\"alert\">&times</a> " + message + "</div>"
      $('#bootstrap-messages').append(alert_message)
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

      // On form submit, reload current orderline
      var that = this
      $("#formSubmit").click(function() {
        setTimeout(function() {
          that.loadOrderLine()
        }, 500) // I hope 500ms is enough to wait for a POST request to complete.
      })
    },

    handleJoin: function(orderline) {
        $.ajax({
        url: api_base + "orderlines/" + this.props.olid + "/join/",
        beforeSend: function(xhr) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        method: 'put',
        success: function(result) {
          this.generateAlert('info', 'Joined orderline')
          var users = this.state.users
          users.push({username: username})
          this.setState({users: users})
        }.bind(this),
        error: function(xhr, err, status) {
          this.generateAlert('danger', 'Failed to join orderline: ' + xhr.responseText)
          console.log("Something went wrong.", xhr, err, status)
        }.bind(this)
      })
    },

    handleLeave: function(orderline) {
        $.ajax({
        url: api_base + "orderlines/" + this.props.olid + "/leave/",
        beforeSend: function(xhr) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        method: 'put',
        success: function(result) {
          this.generateAlert('info', 'Left orderline')
          var users = this.state.users
          users.pop(username)
          this.setState({users: users})
        }.bind(this),
        error: function(xhr, err, status) {
          console.log("Something went wrong.", xhr, err, status)
        }.bind(this)
      })
    },

    render: function() {
        var is_in = false
        for (var i = 0; i < this.state.users.length; i++) {
            if (this.state.users[i].username === username) {
                is_in = true
            }
        }
        var can_join = (this.props.can_join ||
        (!is_in && (this.state.orderline.creator !== username && this.state.orderline.creator !== user)))

        var deleteButton =  this.state.orderline.creator === username || this.state.orderline.creator === user ?
            <IconButton
                value="trash-o" type="danger" btnsize="btn-sm"
                clickHandler={this.handleRemove.bind(this, this.state.orderline)} /> : ""
        var editButton = (is_in || this.state.orderline.creator === username || this.state.orderline.creator === user) ?
            <IconButton
                value="pencil-square-o" type="primary" btnsize="btn-sm"
                clickHandler={this.handleEdit.bind(this, this.state.orderline)} /> : ""
        var joinButton = (can_join) ?
            <IconButton
                value="sign-in" type="primary" btnsize="btn-sm"
                clickHandler={this.handleJoin.bind(this, this.state.orderline)} /> : ""
        var leaveButton = (is_in) ?
            <IconButton
                value="sign-out" type="danger" btnsize="btn-sm"
                clickHandler={this.handleLeave.bind(this, this.state.orderline)} /> : ""

        var users = this.state.users.map(function(user) {
            return (
                <span key={user.id}>{user.username} </span>
            )
        })
        return (
            <tr className={this.state.hideOrderLine ? 'hide' : ''} id={"orderline-" + this.state.orderline.id}>
                <td><b>{this.state.orderline.creator}</b> {users}</td>
                <td>{this.state.orderline.menu_item}</td>
                <td>{this.state.orderline.soda}</td>
                <td>{this.state.orderline.extras}</td>
                <td>{this.state.orderline.price}</td>
                <td>{joinButton}<div className="btn-group">{editButton} {leaveButton} {deleteButton}</div></td>
            </tr>
        );
    }
});

window.OrderLine = OrderLine
module.exports = OrderLine