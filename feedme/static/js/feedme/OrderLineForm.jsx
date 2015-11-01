var OrderLineForm = React.createClass({
    getInitialState: function() {
      return {
        users: []
      }
    },

    componentDidMount: function() {
      $.ajax({
        url: api_base + "orderlines/",
        method: 'OPTIONS',
        success: function(success) {
            console.log(success)
            var users = success.actions.POST.users.choices
            console.log(users)
            this.setState({users: users})
        }.bind(this),
        error: function(xhr, status, err) {
            console.log(xhr, status, err)
        }.bind(this)
      })
    },

    handleSubmit: function(e) {
      e.preventDefault();

      // Get a list of users id's (buddies)
      var users = []
      var users_list = $('#users_list').children()
      for (var i = 0; i < users_list.length; i++) {
        console.log(users_list[i], users_list[i].value)
        if (this.refs.users.value === users_list[i].value) {
          users.push(parseInt(users_list[i].innerHTML))
        }
      }

      console.log("pre ", users)
      if (users.length > 0) {
        users = $.parseJSON(users)
      }
      console.log("post", users)

      this.props.onOrderLineSubmit({
          id: this.refs.id.value,
          menu_item: this.refs.menu_item.value,
          soda: this.refs.soda.value,
          extras: this.refs.extras.value,
          price: this.refs.price.value,
          users: users
      });
      // Reset all the stuff
      this.refs.id.value = "";
      this.refs.menu_item.value = "";
      this.refs.soda.value = "";
      this.refs.extras.value = "";
      this.refs.price.value = "";
      this.refs.users.value = "";
      return;
    },

    render: function() {
        var users = this.state.users.map(function (user) {
        return (
            <option key={user.value} value={user.display_name}>{user.value}</option>
          )
        })
        return (
            <div>
              <h3>New</h3>
              <div className="col-md-12">
                <form className="form-inline orderLineForm" onSubmit={this.handleSubmit}>
                  <input type="number" id="id" ref="id" hidden />
                  <div className="form-group">
                    <label className="sr-only" htmlFor="menu_item">Menu item</label>
                    <input type="text" className="form-control" placeholder="Menu item" id="menu_item" ref="menu_item" />
                  </div>
                  <div className="form-group">
                    <label className="sr-only" htmlFor="soda">Soda</label>
                    <input type="text" className="form-control" placeholder="Soda" id="soda" ref="soda" />
                  </div>
                  <div className="form-group">
                    <label className="sr-only" htmlFor="extras">Extras</label>
                    <input type="text" className="form-control" placeholder="Extras" id="extras" ref="extras" />
                  </div>
                  <div className="form-group">
                    <label className="sr-only" htmlFor="price">Price</label>
                    <input type="number" className="form-control" placeholder="Price" id="price" ref="price" />
                  </div>
                  <div className="form-group">
                    <label className="sr-only" htmlFor="users">Additional users</label>
                    <input type="text" list="users_list" className="form-control" placeholder="Additional users" id="users" ref="users" />
                    <datalist id="users_list">
                        {users}
                    </datalist>
                  </div>
                  <input type="submit" value="Save" id="formSubmit" className="btn btn-success btn-sm" />
                </form>
              </div>
            </div>
        );
    }
});

window.OrderLineForm = OrderLineForm
module.exports = OrderLineForm