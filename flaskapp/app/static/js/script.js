let sourceSquare = null;
let showPieces = true;

const modal = document.getElementById("gameOverModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const closeModalX = document.getElementById("closeModal");
const newGameModalBtn = document.getElementById("newGameModal");

const btn = document.getElementById("showBoard");

btn.addEventListener("mousedown", onPress);
btn.addEventListener("touchstart", onPress);

btn.addEventListener("mouseup",   onRelease);
btn.addEventListener("mouseleave", onRelease);  // in case pointer drifts off
btn.addEventListener("touchend",  onRelease);
btn.addEventListener("touchcancel", onRelease);

function onPress(e) {
  e.preventDefault();           // prevent any click-through
  showPieces = false;           // hide while held
  updateBoard();
  btn.textContent = "Show Pieces";
}

function onRelease(e) {
  showPieces = true;            // show again on release
  updateBoard();
  btn.textContent = "Hide Pieces";
}


const showModal = () => {
  modal.classList.add("show");
};

const hideModal = () => {
  modal.classList.remove("show");
};

window.onclick = (event) => {
  if (event.target === modal) {
    hideModal();
  }
};

closeModalX.onclick = hideModal;
closeModalBtn.onclick = hideModal;

newGameModalBtn.onclick = async () => {
  hideModal();
  localStorage.clear();
  await startNewGame();
};

const startNewGame = async () => {
  $("#cover-spin").show();
  $("#blueScore").text("0");
  $("#redScore").text("0");
  $("#turn").text("Blue");

  await fetch("/api/new_game", {
    method: "POST",
  });

  await updateGameState();

  await new Promise((resolve) => setTimeout(resolve, 3000));

  $("#cover-spin").hide();
};

const clearBoard = async () => {
  boardData = {
    board: [],
  };

  localStorage.removeItem("boardState");
  localStorage.removeItem("legalMoves");
  localStorage.removeItem("historyData");

  document.querySelectorAll(".tile").forEach((tile) => {
    tile.innerHTML = "";
    tile.classList.remove("selected", "highlight");
  });

  $("#blueScore").text("0");
  $("#redScore").text("0");
  $("#turn").text("-");
  $("#turn").css("color", "inherit");

  $("#historyTableBody").empty();
  $("#historyContainer").scrollTop(0);
};

const checkGameEnd = () => {
  const noMovesAvailable =
  legalMoves.valid_moves.length === 0 ||
  legalMoves.valid_moves.every(move => move.destinations.length === 0);

  if (noMovesAvailable) {
    setTimeout(() => {
      const blueScore = historyData.scores.b;
      const redScore = historyData.scores.r;
      let winner;
      let winnerColor;

      if (blueScore > redScore) {
        winner = "Blue";
        winnerColor = "var(--blue-man)";
      } else if (redScore > blueScore) {
        winner = "Red";
        winnerColor = "var(--red-man)";
      } else {
        winner = "Tie";
        winnerColor = "var(--neutral)";
      }
     
      console.log(historyData)
      const response = fetch("/api/add_game_history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          move_history: historyData.move_history,
          scores: historyData.scores,
          winner: winner,
        }),
      });
  
      document.getElementById("finalBlueScore").textContent = blueScore;
      document.getElementById("finalRedScore").textContent = redScore;
      const modalWinner = document.getElementById("modalWinner");
      modalWinner.textContent = winner;
      modalWinner.style.color = winnerColor;

      showModal();

      document.querySelectorAll(".tile").forEach((tile) => {
        tile.removeEventListener("click", handleSquareClick);
      
      
      });
    }, 2000);
    
  return true;

  }
  return false;
};

const updateGameState = async () => {
  const response = await fetch("/api/board");
  boardData = await response.json();
  localStorage.setItem("boardState", JSON.stringify(boardData));

  const movesResponse = await fetch("/api/valid_moves");
  legalMoves = await movesResponse.json();
  localStorage.setItem("legalMoves", JSON.stringify(legalMoves));

  const historyResponse = await fetch("/api/move_history");
  historyData = await historyResponse.json();
  localStorage.setItem("historyData", JSON.stringify(historyData));

  updateBoard();

  if (historyData.current_turn === "r" && legalMoves.valid_moves.length > 0) {
    setTimeout(async () => {
      await makeRedMove();
    }, 500);
  }

  checkGameEnd();
};

const makeMove = async (source, destination, reasoning = null) => {
  const res = await fetch("/api/valid_moves_with_score");
  validMovesWithScores = await res.json();

  
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

    if (result.error) {
      console.error("Move failed:", result.error);
    }
    else {
      
      const lastMove = historyData.move_history[historyData.move_history.length - 1];
      const source = lastMove[1][0];
      const destination = lastMove[1][1]; 
      const score = lastMove[2];
      const finalMoves = (lastMove[0] === "r")
        ? validMovesWithScores["valid_moves_with_scores"]
        : legalMoves.valid_moves;
      const response = fetch("/api/add_move_history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          color: lastMove[0],
          valid_moves: finalMoves,
          choice: { source: source, destination: destination, score: score },
          reasoning: reasoning,
        }),
      });
    }

    return result;
  } catch (error) {
    console.error("Error making move:", error);
    alert("Failed to make move. Please try again.");
    return { success: false, error: error.message };
  }
};

const updateBoard = () => {
  document.getElementById("board").style.display = "grid";

  boardData.board.forEach((tile) => {
    const [pos, op] = tile.position;
    const tileEl = document.getElementById(`tile-${pos}`);
    tileEl.innerHTML = "";

    // always show the operator text
    const operatorText = document.createElement("p");
    operatorText.className = "tile-text-operator";
    operatorText.textContent = op;
    tileEl.appendChild(operatorText);

    // ONLY render pieces if showPieces is true
    if (tile.piece) {
      const [color, number, isKing] = tile.piece;
    
      const pieceEl = document.createElement("div");
      pieceEl.className = "piece";
      // color‐fill as before
      pieceEl.style.backgroundColor =
        color === "red" ? "var(--red-man)" : "var(--blue-man)";
      
      // new: ghost when showPieces is false
      // you can tweak 0.3 to whatever “faded” opacity you like
      pieceEl.style.opacity = showPieces ? "1" : "0.5";
    
      tileEl.appendChild(pieceEl);
    
      const numText = document.createElement("p");
      numText.className =
        color === "red" ? "tile-text-red" : "tile-text-blue";
      numText.textContent = number;
      // also fade the number
      numText.style.opacity = showPieces ? "1" : "0.5";
      tileEl.appendChild(numText);
    
      if (isKing) {
        const crownImg = document.createElement("img");
        crownImg.src = "/static/img/crown-icon.svg";
        crownImg.alt = "crown";
        crownImg.className = "crown";
        // fade the crown too
        crownImg.style.opacity = showPieces ? "1" : "0.5";
        tileEl.appendChild(crownImg);
      }
    }
  });

  updateGameInfo();
};


const updateGameInfo = () => {
  if (!historyData) return;

  let tbody = $("#historyTableBody");
  tbody.empty();

  historyData.move_history.forEach((move, index) => {
    const [color, [from, to], score] = move;
    const moveText = `${from} → ${to}`;

    tbody.append(
      `<tr>
        <td>${index + 1}</td>
        <td>${color === "b" ? moveText : "-"}</td>
        <td>${color === "r" ? moveText : "-"}</td>
        <td>${score}</td>
      </tr>`,
    );
  });
  $("#historyContainer").scrollTop($("#historyContainer")[0].scrollHeight);

  $("#blueScore").text(historyData.scores.b);
  $("#redScore").text(historyData.scores.r);

  const turnElement = $("#turn");
  const currentTurn = historyData.current_turn === "b" ? "Blue" : "Red";
  turnElement.text(currentTurn);
  turnElement.css(
    "color",
    currentTurn === "Blue" ? "var(--blue-man)" : "var(--red-man)",
  );
};

const handleSquareClick = async (e) => {
  if (historyData.current_turn !== "b") {
    console.log("Not your turn - waiting for Red (AI) to move");
    return;
  }

  const clickedTile = e.target.closest(".tile");
  if (!clickedTile) return;

  const tileNumber = parseInt(clickedTile.getAttribute("tile-number"));
  console.log("Clicked tile number:", tileNumber);

  if (sourceSquare === null) {
    const validPieceMove = legalMoves.valid_moves.find(
      (move) => move.piece_index === tileNumber,
    );

    if (validPieceMove) {
      sourceSquare = tileNumber;
      clickedTile.classList.add("selected");
      showLegalMoves(validPieceMove.destinations);
      console.log("Destinations:", validPieceMove.destinations);
    }
  } else {
    const validMove = legalMoves.valid_moves.find(
      (move) => move.piece_index === sourceSquare,
    );

    const isValidDestination =
      validMove &&
      validMove.destinations.some((directionArray) =>
        Array.isArray(directionArray)
          ? directionArray.includes(tileNumber)
          : directionArray === tileNumber,
      );

    if (isValidDestination) {
      const moveResult = await makeMove(sourceSquare, tileNumber);
      console.log("Move result:", moveResult);

      if (moveResult.success && historyData.current_turn === "r") {
        await makeRedMove();
      }
    }
    clearSelection();
  }
};

async function gameLoop() {
  checkGameEnd();

  if (historyData.current_turn === "b") {
    await new Promise(resolve => setTimeout(resolve, 500));
    await makeMinMaxMove();
  } else {
    await new Promise(resolve => setTimeout(resolve, 500));
    await makeRedMove();
  }


  if (!checkGameEnd()) {
    gameLoop();
  }
}

const makeRedMove = async () => {
  $("#cover-spin").show();

  const currentBoard = boardData.array_board;
  const jsonboard = JSON.stringify(boardData.board);
  console.log("JSON Board: ", jsonboard);

  const aiResponse = await fetch("/api/proxy_ai_move", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      board: currentBoard,
      jsonboard: jsonboard,
    }),
  });

  if (!aiResponse.ok) {
    throw new Error(`HTTP error! status: ${aiResponse.status}`);
  }

  const aiResult = await aiResponse.json();
  console.log("AI recommended move:", aiResult);

  const source = aiResult.source;
  const destination = aiResult.destination;
  const reason = aiResult.reason;
  const moveResult = await makeMove(source, destination, reason);

  await new Promise((resolve) => setTimeout(resolve, 3000));

  $("#cover-spin").hide();
  return moveResult;
};


const makeMinMaxMove = async () => {
  $("#cover-spin").show();

  const minmaxResponse = await fetch("/api/minimax_move", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!minmaxResponse.ok) {
    throw new Error(`HTTP error! status: ${minmaxResponse.status}`);
  }

  const aiResult = await minmaxResponse.json();
  console.log("AI recommended move:", aiResult);

  const source = aiResult.source;
  const destination = aiResult.destination;

  const moveResult = await makeMove(source, destination);

  await new Promise((resolve) => setTimeout(resolve, 3000));

  $("#cover-spin").hide();
  return moveResult;
};

const showLegalMoves = (destinations) => {
  document.querySelectorAll(".highlight").forEach((tile) => {
    tile.classList.remove("highlight");
  });

  if (destinations) {
    if (Array.isArray(destinations) && !Array.isArray(destinations[0])) {
      destinations.forEach((movePosition) => {
        const tile = document.getElementById(`tile-${movePosition}`);
        if (tile) tile.classList.add("highlight");
      });
    } else if (Array.isArray(destinations)) {
      destinations.forEach((directionArray) => {
        if (Array.isArray(directionArray)) {
          directionArray.forEach((movePosition) => {
            const tile = document.getElementById(`tile-${movePosition}`);
            if (tile) tile.classList.add("highlight");
          });
        }
      });
    }
  }
};

const clearSelection = () => {
  sourceSquare = null;
  document.querySelectorAll(".selected, .highlight").forEach((tile) => {
    tile.classList.remove("selected", "highlight");
  });
};

$(document).ready(async () => {
  const savedBoard = localStorage.getItem("boardState");
  const savedMoves = localStorage.getItem("legalMoves");
  const savedHistory = localStorage.getItem("historyData");

  if (savedBoard && savedMoves && savedHistory) {
    boardData = JSON.parse(savedBoard);
    legalMoves = JSON.parse(savedMoves);
    historyData = JSON.parse(savedHistory);
    updateBoard();
  } else {
    await updateGameState();
  }

  document.querySelectorAll(".tile").forEach((tile) => {
    tile.addEventListener("click", handleSquareClick);
  });

  document.getElementById("newGame").addEventListener("click", async () => {
    localStorage.clear();
    await startNewGame();
  });
  
  document.getElementById("clearBoard").addEventListener("click", async () => {
    localStorage.clear(); 
    await clearBoard();
  });
  
  document.getElementById("miniMaxPlayer").addEventListener("click", async () => {
    localStorage.clear();
    await startNewGame();    
    gameLoop();
  });

  $("#newGameModal").on("click", async () => {
    $("#gameOverModal").modal("hide");
    localStorage.clear();
    await startNewGame();
  });
});
