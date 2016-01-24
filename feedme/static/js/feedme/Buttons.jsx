var Button = React.createClass({
    render: function() {
        return (
            <button className={"btn btn-" + this.props.type + " btn-sm"} onClick={this.props.clickHandler}>{this.props.value}</button>
        )
    }
})

window.Button = Button
module.exports = Button