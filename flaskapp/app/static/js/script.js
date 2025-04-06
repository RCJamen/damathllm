let light = getComputedStyle(document.body).getPropertyValue("--light");
let dark = getComputedStyle(document.body).getPropertyValue("--dark");
let blueManColor = getComputedStyle(document.body).getPropertyValue(
  "--blue-man",
);
let redManColor = getComputedStyle(document.body).getPropertyValue("--red-man");
let redKingColor = getComputedStyle(document.body).getPropertyValue(
  "--red-king",
);
let blueKingColor = getComputedStyle(document.body).getPropertyValue(
  "--blue-king",
);
let redColor = getComputedStyle(document.body).getPropertyValue("--red");

// Constants
let boardData = null;
let legalMoves = null;
let historyData = null;
let turn = "";
let sourceSquare = null;
const crown_icon = $("#board").attr("crown_icon");

// API Requests
const startNewGame = async () => {
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
  const result = await response.json();
  await updateGameState();
  return result;
};

// Board Update Functions
const updateBoard = () => {
  // Hide start message and show board
  document.getElementById("startGameMessage").style.display = "none";
  document.getElementById("board").style.display = "grid";

  // Update board with pieces
  boardData.board.forEach((tile) => {
    const position = tile.position[0];
    const operator = tile.position[1];
    const tileElement = document.getElementById(`tile-${position}`);
    const textElement = document.getElementById(`tile-${position}-text`);

    // Clear any existing pieces
    tileElement.className = "tile";
    if ((position + Math.floor(position / 8)) % 2 === 0) {
      tileElement.classList.add("dark-tile");
    } else {
      tileElement.classList.add("light-tile");
    }

    textElement.textContent = operator;

    if (tile.piece) {
      const [color, number, isKing] = tile.piece;
      tileElement.classList.add(`piece-${color}`);
      textElement.textContent = `${operator} ${number}`;
      if (isKing) {
        tileElement.classList.add("king");
      }
    }
  });

  updateHistory();
  $("#turn").text(turn);
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
    sourceSquare = tileNumber;
    clickedTile.classList.add("selected");
    showLegalMoves(tileNumber);
  } else {
    if (legalMoves.includes(tileNumber)) {
      await makeMove(sourceSquare, tileNumber);
    }
    clearSelection();
  }
};

const showLegalMoves = (sourcePosition) => {
  // Clear previous highlights
  document.querySelectorAll(".highlight").forEach((tile) => {
    tile.classList.remove("highlight");
  });

  // Show new legal moves
  if (legalMoves) {
    legalMoves.forEach((movePosition) => {
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
