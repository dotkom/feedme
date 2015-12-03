var OrderLineForm = React.createClass({
    getInitialState: function() {
      return {
        users: []
      }
    },

    componentDidMount: function() {
    },

    handleSubmit: function(e) {
      e.preventDefault();

      this.props.onOrderLineSubmit({
          id: this.refs.id.value,
          menu_item: this.refs.menu_item.value,
          soda: this.refs.soda.value,
          extras: this.refs.extras.value,
          price: this.refs.price.value
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
        return (
            <div className="col-md-12">
              <h3>New orderline</h3>
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
                  <div className="form-group hidden">
                    <label className="sr-only" htmlFor="users">Additional users</label>
                    <input type="text" className="form-control" placeholder="Additional users" id="users" ref="users" disabled />
                  </div>
                  <IconButton value="floppy-o" btnid="formSubmit" type="success" btnsize="primary" />
                </form>
              </div>
            </div>
        );
    }
});

window.OrderLineForm = OrderLineForm
module.exports = OrderLineForm