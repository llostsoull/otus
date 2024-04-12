package homework.arch.userservice.config;

import java.util.List;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import io.swagger.v3.oas.models.ExternalDocumentation;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.*;

@Configuration
public class SwaggerConfig {
    @Bean
    public OpenAPI usersOpenAPI() {
        return new OpenAPI()
            .info(new Info().title("User Service API")
                .description("This is simple client API")
                .version("1.0.0").contact(new Contact().email("schetinnikov@gmail.com"))
            )
            .externalDocs(new ExternalDocumentation()
                .description("Otus SwaggerHub API Auto Mocking")
                .url("https://app.swaggerhub.com/apis/otus55/users/1.0.0")
            )
            .servers(List.of(
                new Server().url("/").description("Dev service"),
                new Server().url("http://arch.homework").description("Release service")
            ));
    }
}