import time
from locust import HttpUser, task, between


class UsuarioAPI(HttpUser):
    wait_time = between(1, 3)

    def _get_paginado(self, ruta, nombre):
        with self.client.get(
            f"{ruta}?page=1&per_page=100",
            name=nombre,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                return response.failure(f"HTTP {response.status_code}")
            try:
                if "data" not in response.json():
                    return response.failure("Falta el campo 'data'")
            except ValueError:
                return response.failure("JSON inválido")
            response.success()

    @task(4)
    def listado_usuarios(self):
        self._get_paginado("/api/users", "GET /api/users")

    @task(3)
    def correos_usuarios(self):
        self._get_paginado("/api/users/emails", "GET /api/users/emails")

    @task(2)
    def usuarios_mayores_veinte(self):
        self._get_paginado("/api/users/over-twenty", "GET /api/users/over-twenty")

    @task(1)
    def crear_lote(self):
        uid = time.time_ns()
        usuarios = [
            {
                "name": f"Usuario Locust {i} {uid}",
                "email": f"locust{i}_{uid}@test.com",
                "birth_date": f"200{i}-01-01",
                "password": "Password123",
            }
            for i in range(3)
        ]

        with self.client.post(
            "/api/users/bulk",
            json={"users": usuarios},
            name="POST /api/users/bulk",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                return response.failure(f"HTTP {response.status_code}")
            try:
                if len(response.json().get("users", [])) != 3:
                    return response.failure("No se crearon 3 usuarios")
            except ValueError:
                return response.failure("JSON inválido")
            response.success()