const modal = new bootstrap.Modal(
    document.getElementById("modalConfirmacao")
);

let entregaSelecionada = null;

document
    .querySelectorAll(".btn-confirmar")
    .forEach(botao => {

        botao.addEventListener("click", function () {

            entregaSelecionada = this.dataset.id;

            document
                .getElementById("modalFuncionario")
                .innerText = this.dataset.funcionario;

            const lista =
                document.getElementById("listaEpis");

            lista.innerHTML = "";

            const epis =
                this.closest(".card")
                    .querySelector(".lista-epis")
                    .dataset.epis
                    .split("|");

            epis.forEach(function (epi) {

                if (epi.trim() !== "") {

                    lista.innerHTML += `
                        <li class="list-group-item">
                            🦺 ${epi}
                        </li>
                    `;

                }

            });

            const botaoBiometria =
                document.getElementById("btnBiometria");

            const statusBiometria =
                document.getElementById(
                    "statusBiometria"
                );

            botaoBiometria.style.display =
                "inline-block";

            botaoBiometria.disabled = false;

            statusBiometria.style.display = "none";
            statusBiometria.innerHTML = "";

            modal.show();

        });

    });


document
    .getElementById("btnBiometria")
    .addEventListener("click", function () {

        this.style.display = "none";
        this.disabled = true;

        const statusBiometria =
            document.getElementById(
                "statusBiometria"
            );

        statusBiometria.style.display = "block";

        statusBiometria.innerHTML = `
            <div class="alert alert-info">
                Encoste o dedo cadastrado no leitor...
            </div>
        `;

        validarBiometria();

    });


function validarBiometria() {

    fetch("/terminal/validar-biometria/", {

        method: "POST",

        headers: {
            "X-CSRFToken":
                document.getElementById("csrf").value,

            "Content-Type":
                "application/x-www-form-urlencoded"
        },

        body:
            "entrega=" +
            encodeURIComponent(entregaSelecionada)

    })

    .then(async resposta => {

        let dados;

        try {
            dados = await resposta.json();
        } catch {
            throw new Error(
                "O servidor retornou uma resposta inválida."
            );
        }

        if (!resposta.ok) {
            throw new Error(
                dados.erro ||
                "Não foi possível validar a biometria."
            );
        }

        return dados;

    })

    .then(dados => {

        if (!dados.sucesso) {
            throw new Error(
                dados.erro ||
                "Biometria não confirmada."
            );
        }

        document
            .getElementById("statusBiometria")
            .innerHTML = `
                <div class="alert alert-success">
                    Biometria confirmada com sucesso!
                </div>
            `;

        setTimeout(function () {

            modal.hide();

            location.reload();

        }, 1200);

    })

    .catch(erro => {

        console.error(erro);

        document
            .getElementById("statusBiometria")
            .innerHTML = `
                <div class="alert alert-danger">
                    ${escaparHtml(erro.message)}
                </div>
            `;

        const botaoBiometria =
            document.getElementById("btnBiometria");

        botaoBiometria.style.display =
            "inline-block";

        botaoBiometria.disabled = false;

    });

}


function escaparHtml(texto) {

    const elemento =
        document.createElement("div");

    elemento.textContent = texto;

    return elemento.innerHTML;

}