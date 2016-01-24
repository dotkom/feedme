var Balance = React.createClass({
    getInitialState: function() {
        return {balance: 0}
    },

    componentDidMount: function() {
        $.ajax({
            url: '/' + this.props.url + 'balance/' + user_id + '/',
            method: 'get',
            success: function(result) {
                console.log('balance', result)
                this.setState({balance: result.balance})
            }.bind(this),
            error: function(xhr, status, err) {
                console.log(xhr, status, err)
            }.bind(this)
        })
    },

    render: function() {
        var balance = Math.round(this.state.balance * 100) / 100
        return (
            <span>
                {this.props.username}: {balance} kr
            </span>
        )
    }
})

window.Balance = Balance
module.exports = Balance