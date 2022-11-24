"""def OptimizeCuttingStock_Dummy(orders):
    # Dummy function to test the API
    # Returns a list of orders belonging to a base panel of length 12450

    # Get all orders
    orders = Order.query.filter_by(root_order_id=root).all()

    # initialize base panel
    panels = [3100161, 3100162, 3100163, 3100164, 3100165, 3100165, 3100167,
              3100168, 3100169, 3100170]
    base_length = 12450
    cum_length = 0
    panel_index = 0


    # Loop until all panels are used and panels list is empty
    while len(orders) > 0 and len(panels) > 0:
        for order in orders:
            if cum_length + order.length <= base_length:

                # Assign order to base panel
                order.base_panel_id = panels[0]

                # Update cumulative length
                cum_length += order.length
            else:
                # Remove base panel from list
                panels.pop(0)

                # Assign order to base panel
                order.base_panel_id = panels[panel_index]
                cum_length = order.length




"""