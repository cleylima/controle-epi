const modal = new bootstrap.Modal(
    document.getElementById("modalConfirmacao")
);

let entregaSelecionada = null;

document.querySelectorAll(".btn-confirmar").forEach(botao => {

    botao.addEventListener("click", function () {

        entregaSelecionada = this.dataset.id;

        document.getElementById("modalFuncionario").innerText =
            this.dataset.funcionario;

        const lista = document.getElementById("listaEpis");

        lista.innerHTML = "";

        const epis =
            this.closest(".card")
                .querySelector(".lista-epis")
                .dataset.epis
                .split("|");

        epis.forEach(function(epi){

            if(epi.trim() !== ""){

                lista.innerHTML += `
                    <li class="list-group-item">
                        🦺 ${epi}
                    </li>
                `;

            }

        });

        document.getElementById("btnBiometria").style.display="block";
        document.getElementById("statusBiometria").style.display="none";

        modal.show();

    });

});

document
.getElementById("btnBiometria")
.addEventListener("click", function(){

    this.style.display="none";

    document
    .getElementById("statusBiometria")
    .style.display="block";

    iniciarLeitura();

});

function iniciarLeitura(){

    console.log("Aguardando digital...");

    setTimeout(function(){

        confirmarEntrega();

    },3000);

}

function confirmarEntrega(){

    fetch("/terminal/confirmar/",{

        method:"POST",

        headers:{
            "X-CSRFToken":
                document.getElementById("csrf").value,

            "Content-Type":
                "application/x-www-form-urlencoded"

        },

        body:
            "entrega=" + entregaSelecionada

    })

    .then(res=>res.json())

    .then(dados=>{

        if(dados.sucesso){

            location.reload();

        }

    });

}