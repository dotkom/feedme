var Balance = require('./Balance.jsx')

var Button = require('./Buttons.jsx')

var IconButton = require('./IconButton.jsx')

var Order = require('./Order.jsx')

var OrderLine = require('./OrderLine.jsx')

var OrderLineList = require('./OrderLineList.jsx')

var OrderLineForm = require('./OrderLineForm.jsx')


ReactDOM.render(
    <Order apiroot={"../feedme-api/"} url={"/feedme-api/orderlines/?order=" + order} orderid={order} />,
    document.getElementById("feedme-main")
);