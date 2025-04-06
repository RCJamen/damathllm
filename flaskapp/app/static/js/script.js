let sourceSquare = null;

// API Requests
const startNewGame = async () => {
  $("#blueScore").text("0");
  $("#redScore").text("0");
  $("#turn").text("Blue");
  await fetch("/api/new_game", {
    method: "POST",
  });
  await updateGameState();
};

const updateGameState = async () => {
  // Get board data
  const response = await fetch("/api/board");
  boardData = await response.json();
  // Get valid moves
  const movesResponse = await fetch("/api/valid_moves");
  legalMoves = await movesResponse.json();
  // Get move history
  const historyResponse = await fetch("/api/move_history");
  historyData = await historyResponse.json();

  updateBoard();
};

const makeMove = async (source, destination) => {
  try {
    const response = await fetch("/api/move", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        source: source,
        destination: destination,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    await updateGameState();

    // Optionally handle the result
    if (result.success) {
      console.log("Move successful");
    } else if (result.error) {
      console.error("Move failed:", result.error);
    }

    return result;
  } catch (error) {
    console.error("Error making move:", error);
    // Optionally show error to user
    alert("Failed to make move. Please try again.");
    return { success: false, error: error.message };
  }
};

const updateBoard = () => {
  document.getElementById("board").style.display = "grid";

  boardData.board.forEach((tile) => {
    const position = tile.position[0];
    const operator = tile.position[1];
    const tileElement = document.getElementById(`tile-${position}`);

    tileElement.innerHTML = "";

    const operatorText = document.createElement("p");
    operatorText.className = "tile-text-operator";
    operatorText.textContent = operator;
    tileElement.appendChild(operatorText);

    if (boardData.scores) {
      $("#blueScore").text(boardData.scores.blue);
      $("#redScore").text(boardData.scores.red);
    }

    if (tile.piece) {
      const [color, number, isKing] = tile.piece;

      const pieceElement = document.createElement("div");
      pieceElement.className = "piece";
      pieceElement.id = `piece-${position}`;
      pieceElement.style.backgroundColor =
        color === "red" ? "var(--red-man)" : "var(--blue-man)";
      tileElement.appendChild(pieceElement);

      const numberText = document.createElement("p");
      numberText.id = `tile-${position}-text`;
      numberText.className =
        color === "red" ? "tile-text-red" : "tile-text-blue";
      numberText.textContent = number;
      tileElement.appendChild(numberText);

      if (isKing) {
        const crownImg = document.createElement("img");
        crownImg.src = "/static/images/crown.svg"; // Make sure this path is correct
        crownImg.alt = "crown";
        crownImg.className = "crown";
        tileElement.appendChild(crownImg);
      }
    }
  });

  updateHistory();
  $("#turn").text(boardData.turn);
};

const updateHistory = () => {
  if (!historyData) return;
  let tbody = $("#historyTableBody");
  tbody.empty();

  historyData.move_history.forEach((move, index) => {
    tbody.append(
      `<tr>
        <td>${index + 1}</td>
        <td>${move.blue || "-"}</td>
        <td>${move.red || "-"}</td>
    </tr>`,
    );
  });
  $("#historyContainer").scrollTop($("#historyContainer")[0].scrollHeight);
};

// Event Handlers
const handleSquareClick = async (e) => {
  const clickedTile = e.target.closest(".tile");
  if (!clickedTile) return;

  const tileNumber = parseInt(clickedTile.getAttribute("tile-number"));

  if (!sourceSquare) {
    const validPieceMove = legalMoves.valid_moves.find(
      (move) => move.piece_index === tileNumber,
    );

    if (validPieceMove) {
      sourceSquare = tileNumber;
      clickedTile.classList.add("selected");
      showLegalMoves(validPieceMove.destinations);
    }
  } else {
    const validMove = legalMoves.valid_moves.find(
      (move) => move.piece_index === sourceSquare,
    );

    if (validMove && validMove.destinations.includes(tileNumber)) {
      const moveResult = await makeMove(sourceSquare, tileNumber);
      if (!moveResult.success) {
        // Handle failed move
        console.error("Move failed:", moveResult.error);
      }
    }
    clearSelection();
  }
};

const showLegalMoves = (destinations) => {
  // Clear previous highlights
  document.querySelectorAll(".highlight").forEach((tile) => {
    tile.classList.remove("highlight");
  });

  // Show new legal moves
  if (destinations && destinations.length > 0) {
    destinations.forEach((movePosition) => {
      const tile = document.getElementById(`tile-${movePosition}`);
      if (tile) tile.classList.add("highlight");
    });
  }
};

const clearSelection = () => {
  sourceSquare = null;
  document.querySelectorAll(".selected, .highlight").forEach((tile) => {
    tile.classList.remove("selected", "highlight");
  });
};

// Initialize
$(document).ready(() => {
  // Add click handlers to tiles
  document.querySelectorAll(".tile").forEach((tile) => {
    tile.addEventListener("click", handleSquareClick);
  });

  // Add click handler to new game button
  document.getElementById("newGame").addEventListener("click", startNewGame);
});
