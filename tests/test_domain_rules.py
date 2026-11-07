"""Pruebas unitarias del dominio: Value Objects, Specifications, State Machines y Entidades.

Cada prueba indica la regla (RN) o criterio de aceptación (CA) del BRD que verifica.
No usan base de datos ni API.
"""
from datetime import datetime, timedelta

import pytest

from src.domain.entities import Cliente, CotizacionFormal, Cuadrilla, OrdenDeServicio
from src.domain.events import AccesoDenegadoRegistrado, AusenciaReportada, CotizacionAceptada, ServicioCerrado
from src.domain.exceptions import AutorizacionRequerida, ConflictoDeAgenda, DomainError, TransicionInvalida
from src.domain.specifications import (
    CancelacionSinPenalizacionSpec,
    ClienteSuperaLimiteReprogramacionesSpec,
    CotizacionDentroDeLimiteCoordinadorSpec,
    CuadrillaDisponibleSpec,
    DescuentoAutorizablePorCoordinadorSpec,
    MontoDentroDeLimiteSpec,
    SuperficieDentroDeLimiteSpec,
)
from src.domain.state_machines import (
    CotizacionStateMachine,
    EstadoCotizacion,
    EstadoOrdenServicio,
    OrdenServicioStateMachine,
)
from src.domain.value_objects import Descuento, FirmaConformidad, Monto, Superficie

INICIO = datetime(2026, 11, 20, 9, 0)


def nueva_cotizacion(m2=120.0, extras=None, **kw) -> CotizacionFormal:
    return CotizacionFormal(
        folio=kw.pop("folio", "COT-1"),
        cliente_nombre="Cliente",
        datos_contacto="8100000000",
        ubicacion="San Nicolás",
        tipo_inmueble="casa",
        superficie=Superficie(m2),
        frecuencia="unica",
        extras_solicitados=extras or [],
        **kw,
    )


def orden_programada(cuadrilla=None) -> OrdenDeServicio:
    orden = nueva_cotizacion().aceptar_por_cliente()
    orden.programar(INICIO, cuadrilla or Cuadrilla(id="C-01", integrantes=["A", "B"]))
    return orden


# ---------------------------------------------------------------- Value Objects
class TestValueObjects:
    def test_monto_no_puede_ser_negativo(self):
        with pytest.raises(DomainError):
            Monto(-1)

    def test_monto_operaciones_son_inmutables(self):
        m = Monto(1000)
        assert m.aplicar_porcentaje(10) == Monto(900)
        assert m.factor(0.5) == Monto(500)
        assert m.sumar(Monto(250.5)) == Monto(1250.5)
        assert m.valor == 1000

    def test_superficie_debe_ser_mayor_a_cero(self):
        with pytest.raises(DomainError, match="mayor a cero"):
            Superficie(0)

    @pytest.mark.parametrize("porcentaje", [-1, 101])
    def test_descuento_fuera_de_rango(self, porcentaje):
        with pytest.raises(DomainError):
            Descuento(porcentaje)

    def test_firma_requiere_nombre(self):
        with pytest.raises(DomainError, match="nombre"):
            FirmaConformidad(nombre_firmante=" ", conformidad=True)

    def test_inconformidad_requiere_motivo(self):
        """CA-11.3: la inconformidad exige motivo."""
        with pytest.raises(DomainError, match="motivo"):
            FirmaConformidad(nombre_firmante="Ana", conformidad=False)

    def test_firma_toma_la_hora_de_creacion(self):
        antes = datetime.utcnow()
        firma = FirmaConformidad(nombre_firmante="Ana", conformidad=True)
        assert firma.fecha_hora >= antes


# ---------------------------------------------------------------- Specifications
class TestSpecifications:
    def test_rn01_descuento_coordinador_hasta_10(self):
        spec = DescuentoAutorizablePorCoordinadorSpec(limite=10)
        assert spec.is_satisfied_by(10)
        assert not spec.is_satisfied_by(10.5)

    def test_rn02_limite_coordinador_combina_superficie_y_monto(self):
        spec = CotizacionDentroDeLimiteCoordinadorSpec(max_m2=300, max_monto=8000)
        assert spec.is_satisfied_by((300, 8000))
        assert not spec.is_satisfied_by((301, 1000))
        assert not spec.is_satisfied_by((100, 8000.01))

    def test_operadores_and_or_not(self):
        superficie = SuperficieDentroDeLimiteSpec(300)
        monto = MontoDentroDeLimiteSpec(8000)
        assert (superficie & monto).is_satisfied_by((200, 5000))
        assert not (superficie & monto).is_satisfied_by((400, 5000))
        assert (superficie | monto).is_satisfied_by((400, 5000))
        assert not (superficie | monto).is_satisfied_by((400, 9000))
        assert (~superficie).is_satisfied_by((400, 0))

    def test_rn04_cancelacion_sin_costo_con_24_horas(self):
        spec = CancelacionSinPenalizacionSpec(horas_minimas=24)
        assert spec.is_satisfied_by((INICIO - timedelta(hours=24), INICIO))
        assert not spec.is_satisfied_by((INICIO - timedelta(hours=23, minutes=59), INICIO))

    def test_rn08_mas_de_dos_reprogramaciones_alerta(self):
        spec = ClienteSuperaLimiteReprogramacionesSpec(max_reprogramaciones=2)
        assert not spec.is_satisfied_by(2)
        assert spec.is_satisfied_by(3)

    def test_ca07_2_cuadrilla_sin_traslape(self):
        spec = CuadrillaDisponibleSpec()
        ocupado = [(INICIO, INICIO + timedelta(hours=2))]
        assert not spec.is_satisfied_by((INICIO + timedelta(hours=1), INICIO + timedelta(hours=3), ocupado))
        assert spec.is_satisfied_by((INICIO + timedelta(hours=2), INICIO + timedelta(hours=4), ocupado))


# ---------------------------------------------------------------- State Machines
class TestStateMachines:
    def test_cotizacion_aceptada_es_estado_final(self):
        with pytest.raises(TransicionInvalida):
            CotizacionStateMachine.transicionar(EstadoCotizacion.ACEPTADA, EstadoCotizacion.BORRADOR)

    def test_pendiente_solo_puede_autorizarse_o_descartarse(self):
        assert CotizacionStateMachine.transicionar(
            EstadoCotizacion.PENDIENTE_AUTORIZACION, EstadoCotizacion.AUTORIZADA
        ) == EstadoCotizacion.AUTORIZADA
        with pytest.raises(TransicionInvalida):
            CotizacionStateMachine.transicionar(EstadoCotizacion.PENDIENTE_AUTORIZACION, EstadoCotizacion.ACEPTADA)

    def test_orden_no_puede_cerrarse_sin_ejecutarse(self):
        with pytest.raises(TransicionInvalida):
            OrdenServicioStateMachine.transicionar(EstadoOrdenServicio.PROGRAMADA, EstadoOrdenServicio.CERRADA_CONFORMIDAD)

    def test_orden_facturada_es_estado_final(self):
        with pytest.raises(TransicionInvalida):
            OrdenServicioStateMachine.transicionar(EstadoOrdenServicio.FACTURADA, EstadoOrdenServicio.PROGRAMADA)


# ---------------------------------------------------------------- Entidades
class TestCliente:
    def test_mismo_cliente_aunque_cambie_el_formato(self):
        assert Cliente("Ana", "81-1234-5678").id == Cliente("Ana", "81 1234 5678").id == "8112345678"
        assert Cliente("Ana", " Ana@Correo.com ").id == "ana@correo.com"

    def test_cliente_requiere_nombre_y_contacto(self):
        with pytest.raises(DomainError):
            Cliente("", "81")


class TestCotizacion:
    def test_us02_sugiere_horas_y_personal(self):
        """CA-02.1: 240 m² a 60 m²/h + 1 h de extra = 5 horas-persona y 2 personas."""
        cot = nueva_cotizacion(240, extras=[{"horas": 1.0, "costo": 500.0}])
        assert cot.horas_persona_sugeridas == 5.0
        assert cot.personal_sugerido == 2
        assert cot.total == Monto(240 * 25 + 500)

    def test_ca01_campos_obligatorios(self):
        with pytest.raises(DomainError, match="obligatorios"):
            CotizacionFormal(
                folio="X", cliente_nombre="C", datos_contacto="", ubicacion="U", tipo_inmueble="casa",
                superficie=Superficie(10), frecuencia="unica", extras_solicitados=[],
            )

    def test_rn02_mas_de_300m2_queda_pendiente_de_gerencia(self):
        assert nueva_cotizacion(301).estado == EstadoCotizacion.PENDIENTE_AUTORIZACION
        assert nueva_cotizacion(300).estado == EstadoCotizacion.BORRADOR

    def test_rn01_descuento_mayor_a_10_bloquea(self):
        cot = nueva_cotizacion(100)
        cot.aplicar_descuento(10, "coordinador", "coord")
        assert cot.total == Monto(2250)
        with pytest.raises(AutorizacionRequerida):
            cot.aplicar_descuento(15, "coordinador", "coord")
        assert cot.estado == EstadoCotizacion.PENDIENTE_AUTORIZACION

    def test_gerencia_puede_aplicar_mas_de_10(self):
        cot = nueva_cotizacion(100)
        cot.aplicar_descuento(20, "gerencia", "renata")
        assert cot.total == Monto(2000)
        assert cot.estado == EstadoCotizacion.BORRADOR

    def test_no_se_envia_ni_acepta_pendiente(self):
        cot = nueva_cotizacion(400)
        with pytest.raises(DomainError):
            cot.enviar_al_cliente()
        with pytest.raises(DomainError):
            cot.aceptar_por_cliente()
        with pytest.raises(DomainError, match="revisión"):
            cot.rechazar_por_cliente()

    def test_autorizada_se_envia_y_se_acepta_generando_evento(self):
        cot = nueva_cotizacion(400)
        cot.autorizar_por_gerencia("renata")
        cot.enviar_al_cliente()
        assert cot.estado == EstadoCotizacion.ENVIADA
        orden = cot.aceptar_por_cliente()
        assert orden.estado == EstadoOrdenServicio.GENERADA
        assert orden.datos_contacto == cot.datos_contacto
        assert isinstance(cot.eventos[-1], CotizacionAceptada)

    def test_aceptada_no_se_edita(self):
        cot = nueva_cotizacion()
        cot.aceptar_por_cliente()
        with pytest.raises(DomainError, match="aceptada"):
            cot.aplicar_descuento(5, "coordinador", "coord")

    def test_gerencia_descarta_y_cliente_rechaza(self):
        cot = nueva_cotizacion(400)
        cot.descartar_por_gerencia("renata")
        assert cot.estado == EstadoCotizacion.RECHAZADA_GERENCIA
        cot2 = nueva_cotizacion()
        cot2.rechazar_por_cliente()
        assert cot2.estado == EstadoCotizacion.RECHAZADA_CLIENTE


class TestOrdenDeServicio:
    def test_ca07_2_no_asigna_cuadrilla_con_traslape(self):
        cuadrilla = Cuadrilla(id="C-01", integrantes=["A"])
        orden_programada(cuadrilla)
        otra = nueva_cotizacion(folio="COT-2").aceptar_por_cliente()
        with pytest.raises(ConflictoDeAgenda, match="traslape"):
            otra.programar(INICIO + timedelta(hours=1), cuadrilla)

    def test_us12_ausencia_sustituye_integrante_y_emite_evento(self):
        cuadrilla = Cuadrilla(id="C-01", integrantes=["A", "B"])
        orden = orden_programada(cuadrilla)
        orden.registrar_ausencia("A", "Incapacidad", "C")
        assert cuadrilla.integrantes == ["B", "C"]
        assert isinstance(orden.eventos[-1], AusenciaReportada)
        with pytest.raises(DomainError, match="motivo"):
            orden.registrar_ausencia("B", " ")

    def test_ca09_2_no_cierra_sin_inicio(self):
        orden = orden_programada()
        with pytest.raises(DomainError, match="inicio"):
            orden.cerrar_servicio(FirmaConformidad("Cliente", True))

    def test_ca10_incidencia_requiere_descripcion_y_foto(self):
        orden = orden_programada()
        orden.registrar_inicio(INICIO)
        orden.documentar_incidencia("daño", "Persiana rota", [])
        with pytest.raises(DomainError, match="fotografía"):
            orden.cerrar_servicio(FirmaConformidad("Cliente", True))

    def test_us11_cierre_con_inconformidad(self):
        orden = orden_programada()
        orden.registrar_inicio(INICIO)
        orden.cerrar_servicio(FirmaConformidad("Cliente", False, "Faltaron ventanas"))
        assert orden.estado == EstadoOrdenServicio.CERRADA_INCONFORMIDAD
        assert isinstance(orden.eventos[-1], ServicioCerrado)

    def test_rn05_acceso_denegado_cobra_100_y_libera_cuadrilla(self):
        cuadrilla = Cuadrilla(id="C-01", integrantes=["A"])
        orden = orden_programada(cuadrilla)
        with pytest.raises(DomainError, match="evidencia"):
            orden.registrar_acceso_denegado(" ")
        orden.registrar_acceso_denegado("foto.jpg")
        assert orden.monto_facturable == orden.precio_total
        assert cuadrilla.estado == "Disponible"
        assert isinstance(orden.eventos[-1], AccesoDenegadoRegistrado)

    def test_rn04_cancelacion_tardia_cobra_50(self):
        orden = orden_programada()
        orden.cancelar(INICIO - timedelta(hours=5))
        assert orden.estado == EstadoOrdenServicio.CANCELADA_CON_CARGO
        assert orden.monto_facturable == orden.precio_total.factor(0.5)

    def test_rn04_fuerza_mayor_no_cobra(self):
        orden = orden_programada()
        orden.cancelar(INICIO - timedelta(hours=5), fuerza_mayor=True)
        assert orden.estado == EstadoOrdenServicio.CANCELADA_SIN_CARGO
        assert orden.monto_facturable == Monto(0)

    def test_cancelar_orden_sin_programar(self):
        orden = nueva_cotizacion().aceptar_por_cliente()
        orden.cancelar(INICIO)
        assert orden.estado == EstadoOrdenServicio.CANCELADA_SIN_CARGO

    def test_rn06_extra_solo_suma_si_el_cliente_autoriza(self):
        orden = orden_programada()
        precio = orden.precio_total
        orden.solicitar_y_autorizar_extra("Terraza", 600, autorizado=False)
        assert orden.precio_total == precio and len(orden.extras) == 1
        orden.solicitar_y_autorizar_extra("Terraza", 600, autorizado=True)
        assert orden.precio_total == precio.sumar(Monto(600))
        with pytest.raises(DomainError, match="descripción"):
            orden.solicitar_y_autorizar_extra(" ", 10, True)

    def test_rn07_recalculo_proporcional_con_evidencia(self):
        orden = orden_programada()
        precio = orden.precio_total
        with pytest.raises(DomainError, match="evidencia"):
            orden.recalcular_por_superficie_mayor(200, [], True)
        with pytest.raises(DomainError, match="mayor"):
            orden.recalcular_por_superficie_mayor(100, ["f.jpg"], True)
        orden.recalcular_por_superficie_mayor(180, ["f.jpg"], autorizado_cliente=False)
        assert orden.precio_total == precio  # el cliente no aceptó: se hace solo lo cotizado
        orden.recalcular_por_superficie_mayor(180, ["f.jpg"], autorizado_cliente=True)
        assert orden.precio_total == precio.factor(180 / 120)

    def test_ajustes_solo_en_servicio_activo(self):
        orden = nueva_cotizacion().aceptar_por_cliente()
        with pytest.raises(DomainError, match="programados"):
            orden.solicitar_y_autorizar_extra("Terraza", 600, True)

    def test_rn09_facturar_servicio_cerrado(self):
        orden = orden_programada()
        orden.registrar_inicio(INICIO)
        orden.cerrar_servicio(FirmaConformidad("Cliente", True))
        with pytest.raises(DomainError, match="folio"):
            orden.facturar(" ")
        orden.facturar("FAC-1")
        assert orden.estado == EstadoOrdenServicio.FACTURADA
        with pytest.raises(TransicionInvalida):
            orden.facturar("FAC-2")
