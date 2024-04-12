package homework.arch.userservice;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import com.fasterxml.jackson.databind.ObjectMapper;

import homework.arch.userservice.dto.User;

@SpringBootTest
@AutoConfigureMockMvc
public class UserControllerTests {

	@Autowired
	private MockMvc mockMvc;
    @Autowired
    private ObjectMapper objectMapper;

	@Test
    public void givenUser_whenAdd_thenStatus201andUserReturned() throws Exception {
        User user = new User();
		user.setUsername("sidorov");
		user.setFirstName("Ivan");
		user.setLastName("sidorov");
		user.setEmail("sidorov@mail.ru");
		user.setPhone("1234567");
        mockMvc.perform(
                post("/user")
                        .content(objectMapper.writeValueAsString(user))
                        .contentType(MediaType.APPLICATION_JSON)
        )
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").isNumber())
                .andExpect(jsonPath("$.username").value("sidorov"));
    }

	@Test
	public void userShouldReturnDefaultOK() throws Exception {
		this.mockMvc.perform(get("/user")).andDo(print()).andExpect(status().isOk());
	}

}
