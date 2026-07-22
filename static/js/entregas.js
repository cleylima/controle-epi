let itensEntrega = [];

const btnAdicionar = document.getElementById("btnAdicionar");

btnAdicionar.addEventListener("click", adicionarItem);

function adicionarItem() {

    const epi = document.getElementById("id_epi");
    const quantidade = document.getElementById("id_quantidade");
    const motivo = document.getElementById("id_motivo");

    if (!epi.value) {
        alert("Selecione um EPI.");
        return;
    }

    itensEntrega.push({

        epi_id: epi.value,
        epi_nome: epi.options[epi.selectedIndex].text,
        quantidade: quantidade.value,
        motivo: motivo.value,
        motivo: motivo.options[motivo.selectedIndex].text

    });

    atualizarTabela();

}

function atualizarTabela() {

    const tbody = document.querySelector("#tabelaItens tbody");

    tbody.innerHTML = "";

    itensEntrega.forEach((item, indice) => {

        tbody.innerHTML += `
            <tr>
                <td>${item.epi_nome}</td>
                <td>${item.quantidade}</td>
                <td>${item.motivo_texto}</td>
                <td>
                    <button
                        type="button"
                        class="btn btn-danger btn-sm"
                        onclick="removerItem(${indice})">
                        ✖
                    </button>
                </td>
            </tr>
        `;

    });

}

function removerItem(indice){

    itensEntrega.splice(indice,1);

    atualizarTabela();

}

document
  .getElementById("formEntrega")
  .addEventListener("submit", function () {
    document.getElementById("itensEntrega").value =
      JSON.stringify(itensEntrega);

    console.log("JSON enviado:", document.getElementById("itensEntrega").value);
  });
