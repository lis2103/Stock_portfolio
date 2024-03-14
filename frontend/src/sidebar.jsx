import React, { useState, useEffect } from "react";
import { Card, CardHeader, Button } from "@nextui-org/react";
import { useNavigate } from "react-router-dom";
import { useUser } from "./UserContext"; // Import the useUser hook

export default function Sidebar() {
  const { user } = useUser(); // Use the user context
  const [portfolioItems, setPortfolioItems] = useState([]);
  const [reloadSidebar, setReloadSidebar] = useState(false); // State to trigger sidebar reload
  const navigate = useNavigate();
  const [hoverIndex, setHoverIndex] = useState(null);
  const [showSearchBox, setShowSearchBox] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [purchasePrice, setPurchasePrice] = useState(""); // State for purchase price
  const [quantity, setQuantity] = useState(""); // State for quantity

  useEffect(() => {
    if (user) {
      fetch(
        `https://mcsbt-integration-416413.lm.r.appspot.com/portfolio/${user.username}`
      )
        .then((response) => response.json())
        .then((data) => {
          setPortfolioItems(data);
        })
        .catch(console.error);
    }
  }, [user, reloadSidebar]); // Include reloadSidebar in dependency array

  useEffect(() => {
    const fetchPercentageChanges = async () => {
      if (portfolioItems.length === 0) return; // Exit if portfolioItems is empty

      const promises = portfolioItems.map((item) =>
        fetch(
          `https://mcsbt-integration-416413.lm.r.appspot.com/${item.ticker}`
        ).then((response) => response.json())
      );

      const results = await Promise.all(promises);
      const updatedItems = portfolioItems.map((item, index) => ({
        ...item,
        stock_info: results[index],
      }));

      setPortfolioItems(updatedItems);
    };

    fetchPercentageChanges().catch(console.error);
  }, [portfolioItems.length]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value.toUpperCase());
  };

  const handleQuantityChange = (e) => {
    // Define handleQuantityChange at the component level
    const value = e.target.value.replace(/[^0-9]/g, "");
    setQuantity(value);
  };

  const handleAddStock = async () => {
    try {
      const response = await fetch(
        `https://mcsbt-integration-416413.lm.r.appspot.com/add-stock/${user.username}/${inputValue}/${quantity}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            purchase_price: parseFloat(purchasePrice),
            quantity: parseInt(quantity),
          }),
        }
      );
      if (!response.ok) {
        throw new Error("Failed to add stock");
      }
      console.log(`Stock ${inputValue} added.`);
      setReloadSidebar(!reloadSidebar); // Trigger sidebar reload
      setShowSearchBox(false); // Close the "Add stock" dialog
      setInputValue(""); // Reset inputValue to empty string
      setQuantity(""); // Reset quantity to empty string
    } catch (error) {
      console.error(error.message);
    }
  };

  const handleRemoveStock = async (ticker) => {
    try {
      const response = await fetch(
        `https://mcsbt-integration-416413.lm.r.appspot.com/remove-stock/${user.username}/${ticker}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!response.ok) {
        throw new Error("Failed to remove ticker");
      }
      console.log(`Ticker ${ticker} removed.`);
      setReloadSidebar(!reloadSidebar); // Trigger sidebar reload
    } catch (error) {
      console.error(error.message);
    }
  };

  return (
    <div style={{ marginLeft: "30px" }}>
      <Card
        className="my-4"
        style={{ width: "200px", backgroundColor: "rgb(55, 55, 61)" }}
        isPressable={true}
        disableRipple={true}
        onPress={() => navigate("/summary")}
      >
        <CardHeader className="flex-col items-center justify-between">
          <h4 className="font-bold">Summary →</h4>
        </CardHeader>
      </Card>

      {portfolioItems.map((item, index) => (
        <div
          style={{ position: "relative", width: "230px", marginBottom: "1rem" }}
          key={index}
        >
          <div
            onMouseEnter={() => setHoverIndex(index)}
            onMouseLeave={() => setHoverIndex(null)}
            style={{
              position: "absolute",
              top: "50%",
              right: "0",
              width: "30px",
              height: "100%",
              cursor: "pointer",
              zIndex: 10,
              transform: "translateY(-50%)",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: "50%",
                transform: "translateY(-50%) translateX(-10%)",
                right: "0",
                padding: "0px",
                fontSize: "20px",
                fontWeight: "normal",
                opacity: hoverIndex === index ? 1 : 0,
                transition: "opacity 0.3s ease-in-out",
                cursor: "pointer", // Add cursor pointer
              }}
              onClick={() => {
                const isConfirmed = window.confirm(
                  `Would you like to remove the ticker ${item.ticker}?`
                );
                if (isConfirmed) {
                  handleRemoveStock(item.ticker);
                }
              }}
            >
              ✕
            </div>
          </div>

          <Card
            isPressable={true}
            disableRipple={true}
            onPress={() => navigate(`/${item.ticker}`)}
            style={{ width: "200px" }}
          >
            <CardHeader className="flex-col items-start justify-between">
              <h4 className="font-bold">{item.ticker}</h4>
              <small>
                {item.stock_info && item.stock_info.percent_change
                  ? `${parseFloat(item.stock_info.percent_change).toFixed(
                      2
                    )}% from previous week`
                  : "Loading..."}
              </small>
            </CardHeader>
          </Card>
        </div>
      ))}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "200px",
        }}
      >
        <Button fullWidth onClick={() => setShowSearchBox(!showSearchBox)}>
          Add stock
        </Button>
        <div
          style={{
            opacity: showSearchBox ? 1 : 0,
            visibility: showSearchBox ? "visible" : "hidden",
            transition: "opacity 0.3s ease-in-out, visibility 0.3s",
            width: "200px",
            marginTop: "15px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "0px",
          }}
        >
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Enter a stock"
            style={{
              fontSize: "14px",
              borderRadius: "10px 10px 0 0", // Round top corners, straight bottom corners
              border: "1px solid #ccc",
              padding: "5px 10px",
              boxSizing: "border-box",
              width: "200px",
            }}
          />

          <input
            type="text"
            value={quantity}
            onChange={handleQuantityChange}
            placeholder="Quantity"
            style={{
              fontSize: "14px",
              borderRadius: "0", // Completely rectangular
              borderTop: "0", // Remove top border to eliminate space
              borderLeft: "1px solid #ccc",
              borderRight: "1px solid #ccc",
              borderBottom: "1px solid #ccc",
              padding: "5px 10px",
              boxSizing: "border-box",
              width: "200px",
            }}
          />

          <Button
            onClick={handleAddStock} // Add onClick handler for adding stock
            style={{
              borderRadius: "0 0 10px 10px", // Straight top corners, rounded bottom corners
              padding: "5px 10px",
              boxSizing: "border-box",
              width: "200px",
              height: "30px",
              fontSize: "14px",
              borderTop: "0", // Remove top border to eliminate space
              borderLeft: "1px solid #ccc",
              borderRight: "1px solid #ccc",
              borderBottom: "1px solid #ccc",
            }}
            aria-label="Confirm entries"
          >
            Confirm
          </Button>
        </div>
      </div>
    </div>
  );
}
