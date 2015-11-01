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
            <div>
              <div className="col-md-2">Ny bestilling</div>
              <div className="col-md-10">
                <form className="form orderLineForm" onSubmit={this.handleSubmit}>
                  <input type="number" id="id" ref="id" hidden />
                  <div className="col-md-2">
                    <input type="text" placeholder="Menu item" id="menu_item" ref="menu_item" />
                  </div>
                  <div className="col-md-2">
                    <input type="text" placeholder="Soda" id="soda" ref="soda" />
                  </div>
                  <div className="col-md-2">
                    <input type="text" placeholder="Extras" id="extras" ref="extras" />
                  </div>
                  <div className="col-md-2">
                    <input type="number" placeholder="Price" id="price" ref="price" />
                  </div>
                  <div className="col-md-2">
                    <input type="submit" value="Save" className="btn btn-success btn-sm" />
                  </div>
                </form>
              </div>
            </div>
        );
    }
});

window.OrderLineForm = OrderLineForm
module.exports = OrderLineForm