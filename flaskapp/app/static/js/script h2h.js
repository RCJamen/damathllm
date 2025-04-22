let sourceSquare = null;
const modal = document.getElementById("gameOverModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const closeModalX = document.getElementById("closeModal");
const newGameModalBtn = document.getElementById("newGameModal");

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
  if (legalMoves.valid_moves.length === 0) {
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

  // if (historyData.current_turn === "r" && legalMoves.valid_moves.length > 0) {
  //   setTimeout(async () => {
  //     await makeRedMove();
  //   }, 500);
  // }

  checkGameEnd();
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

    if (result.success) {
      console.log("Move successful");
    } else if (result.error) {
      console.error("Move failed:", result.error);
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
    const position = tile.position[0];
    const operator = tile.position[1];
    const tileElement = document.getElementById(`tile-${position}`);

    tileElement.innerHTML = "";

    const operatorText = document.createElement("p");
    operatorText.className = "tile-text-operator";
    operatorText.textContent = operator;
    tileElement.appendChild(operatorText);

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
        crownImg.src = "/static/img/crown-icon.svg";
        crownImg.alt = "crown";
        crownImg.className = "crown";
        tileElement.appendChild(crownImg);
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
  // if (historyData.current_turn !== "b") {
  //   console.log("Not your turn - waiting for Red (AI) to move");
  //   return;
  // }

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

      // if (moveResult.success && historyData.current_turn === "r") {
      //   await makeRedMove();
      // }
    }
    clearSelection();
  }
};

const makeRedMove = async () => {
  $("#cover-spin").show();

  const currentBoard = boardData.array_board;

  const aiResponse = await fetch("/api/proxy_ai_move", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      board: currentBoard,
    }),
  });

  if (!aiResponse.ok) {
    throw new Error(`HTTP error! status: ${aiResponse.status}`);
  }

  const aiResult = await aiResponse.json();
  console.log("AI recommended move:", aiResult);

  const source = aiResult.source;
  const destination = aiResult.destination;

  const moveResult = await makeMove(source, destination);

  await updateGameState();

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

  $("#newGameModal").on("click", async () => {
    $("#gameOverModal").modal("hide");
    localStorage.clear();
    await startNewGame();
  });
});
