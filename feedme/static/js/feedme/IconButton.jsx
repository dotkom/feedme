var IconButton = React.createClass({
    render: function() {
        return (
            <button
                className={"btn btn-" + this.props.type + " " + this.props.btnsize}
                onClick={this.props.clickHandler}
                id={this.props.btnid}
                >
                  <i className={"fa " + (this.props.size ? ("fa-" + this.props.size + " ") : " ") + ("fa-" + this.props.value)}></i>
            </button>
        )
    }
})

window.IconButton = IconButton
module.exports = IconButton