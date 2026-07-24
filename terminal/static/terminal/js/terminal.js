document.addEventListener("DOMContentLoaded", () => {
    const LOCAL_BIOMETRIA_URL = "http://127.0.0.1:5055";

    const modalElemento = document.getElementById("modalBiometria");
    const modalBiometria = modalElemento
        ? new bootstrap.Modal(modalElemento)
        : null;

    const nomeFuncionario = document.getElementById("nomeFuncionario");
    const mensagemBiometria = document.getElementById("mensagemBiometria");
    const botaoConfirmar = document.getElementById("btnConfirmarBiometria");

    let entregaSelecionada = null;
    let sessaoAtual = null;
    let consultaStatus = null;

    function obterCookie(nome) {
        const cookies = document.cookie
            ? document.cookie.split(";")
            : [];

        for (const cookie of cookies) {
            const parte = cookie.trim();

            if (parte.startsWith(`${nome}=`)) {
                return decodeURIComponent(
                    parte.substring(nome.length + 1)
                );
            }
        }

        return null;
    }

    function atualizarMensagem(texto, tipo = "info") {
        if (!mensagemBiometria) {
            return;
        }

        mensagemBiometria.className = `alert alert-${tipo}`;
        mensagemBiometria.textContent = texto;
        mensagemBiometria.classList.remove("d-none");
    }

    function limparConsultaStatus() {
        if (consultaStatus) {
            clearInterval(consultaStatus);
            consultaStatus = null;
        }
    }

    function resetarModal() {
        limparConsultaStatus();

        entregaSelecionada = null;
        sessaoAtual = null;

        if (botaoConfirmar) {
            botaoConfirmar.disabled = false;
        }

        if (mensagemBiometria) {
            mensagemBiometria.classList.add("d-none");
            mensagemBiometria.textContent = "";
        }
    }

    async function iniciarSessaoBiometrica() {
        if (!entregaSelecionada) {
            throw new Error("Entrega não selecionada.");
        }

        const resposta = await fetch(
            "/terminal/biometria/iniciar/",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/x-www-form-urlencoded",
                    "X-CSRFToken":
                        obterCookie("csrftoken")
                },
                body: new URLSearchParams({
                    entrega: entregaSelecionada
                })
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok || !dados.sucesso) {
            throw new Error(
                dados.erro ||
                "Não foi possível iniciar a validação biométrica."
            );
        }

        sessaoAtual = dados.sessao;

        return dados;
    }

    async function chamarServicoLocal(sessaoId) {
        const resposta = await fetch(
            `${LOCAL_BIOMETRIA_URL}/validar-sessao`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    sessao: sessaoId,
                    origem: window.location.origin
                })
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok || !dados.sucesso) {
            throw new Error(
                dados.erro ||
                dados.mensagem ||
                "Falha ao acessar o serviço biométrico local."
            );
        }

        return dados;
    }

    async function consultarStatus(sessaoId) {
        const resposta = await fetch(
            `/terminal/biometria/${sessaoId}/status/`,
            {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok || !dados.sucesso) {
            throw new Error(
                dados.erro ||
                "Não foi possível consultar a validação."
            );
        }

        return dados;
    }

    function acompanharStatus(sessaoId) {
        limparConsultaStatus();

        consultaStatus = setInterval(async () => {
            try {
                const dados = await consultarStatus(sessaoId);

                switch (dados.status) {
                    case "pendente":
                        atualizarMensagem(
                            "Aguardando a leitura da digital...",
                            "warning"
                        );
                        break;

                    case "confirmada":
                    case "utilizada":
                        limparConsultaStatus();

                        atualizarMensagem(
                            dados.mensagem ||
                            "Entrega confirmada com sucesso.",
                            "success"
                        );

                        setTimeout(() => {
                            window.location.reload();
                        }, 1200);
                        break;

                    case "rejeitada":
                        limparConsultaStatus();

                        atualizarMensagem(
                            dados.mensagem ||
                            "A digital não corresponde ao funcionário.",
                            "danger"
                        );

                        if (botaoConfirmar) {
                            botaoConfirmar.disabled = false;
                        }
                        break;

                    case "expirada":
                        limparConsultaStatus();

                        atualizarMensagem(
                            "A sessão biométrica expirou. Tente novamente.",
                            "danger"
                        );

                        if (botaoConfirmar) {
                            botaoConfirmar.disabled = false;
                        }
                        break;

                    default:
                        atualizarMensagem(
                            "Processando validação biométrica...",
                            "info"
                        );
                        break;
                }
            } catch (erro) {
                limparConsultaStatus();

                atualizarMensagem(
                    erro.message,
                    "danger"
                );

                if (botaoConfirmar) {
                    botaoConfirmar.disabled = false;
                }
            }
        }, 1000);
    }

    async function executarValidacao() {
        if (!entregaSelecionada) {
            atualizarMensagem(
                "Nenhuma entrega foi selecionada.",
                "danger"
            );
            return;
        }

        if (botaoConfirmar) {
            botaoConfirmar.disabled = true;
        }

        try {
            atualizarMensagem(
                "Criando sessão biométrica...",
                "info"
            );

            const sessao = await iniciarSessaoBiometrica();

            atualizarMensagem(
                "Conectando ao leitor biométrico...",
                "info"
            );

            await chamarServicoLocal(sessao.sessao);

            atualizarMensagem(
                "Coloque o dedo no leitor.",
                "warning"
            );

            acompanharStatus(sessao.sessao);
        } catch (erro) {
            atualizarMensagem(
                erro.message,
                "danger"
            );

            if (botaoConfirmar) {
                botaoConfirmar.disabled = false;
            }
        }
    }

    document
    .querySelectorAll("[data-entrega-id]")
    .forEach((botao) => {
        botao.addEventListener("click", () => {
            resetarModal();

            entregaSelecionada =
                botao.dataset.entregaId;

            const funcionario =
                botao.dataset.funcionarioNome ||
                "Funcionário";

            if (nomeFuncionario) {
                nomeFuncionario.textContent =
                    funcionario;
            }

            const card = botao.closest(".card-entrega");
            const listaEpis =
                document.getElementById("listaEpis");

            if (listaEpis) {
                listaEpis.innerHTML = "";

                const elementosEpi =
                    card?.querySelectorAll(
                        ".lista-epis .epi-item"
                    ) || [];

                elementosEpi.forEach((elemento) => {
                    const item =
                        document.createElement("li");

                    item.className =
                        "list-group-item";

                    item.textContent =
                        elemento.textContent.trim();

                    listaEpis.appendChild(item);
                });
            }

            if (modalBiometria) {
                modalBiometria.show();
            }
        });
    });

    if (botaoConfirmar) {
        botaoConfirmar.addEventListener(
            "click",
            executarValidacao
        );
    }

    if (modalElemento) {
        modalElemento.addEventListener(
            "hidden.bs.modal",
            resetarModal
        );
    }
});